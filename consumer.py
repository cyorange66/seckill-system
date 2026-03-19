import asyncio
import json
import time
import logging
from aio_pika import connect_robust, IncomingMessage, ExchangeType
from app.core.database import async_session_local
from app.models.order import Order
from sqlalchemy import insert

# 基本日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderConsumer:
    def __init__(self):
        self.queue_name = "order_queue"
        self.buffer = []            # 存放数据
        self.message_buffer = []    # 存放消息对象，用于后续批量 ACK
        self.last_flush_time = time.time()
        self.lock = asyncio.Lock()  # 防止并发写入 DB

    async def flush_to_db(self):
        """将缓冲区内的订单批量写入 MySQL，成功后批量 ACK"""
        async with self.lock: # 确保同一时间只有一个写入任务在跑
            if not self.buffer:
                return

            orders_to_save = self.buffer.copy()
            messages_to_ack = self.message_buffer.copy()
            
            self.buffer.clear()
            self.message_buffer.clear()
            self.last_flush_time = time.time()
            
            try:
                # 1. 批量落库
                async with async_session_local() as db:
                    stmt = insert(Order).values(orders_to_save)
                    await db.execute(stmt)
                    await db.commit()
                
                # 2. 只有入库成功，才逐个确认消息
                for msg in messages_to_ack:
                    await msg.ack()
                
                logger.info(f"Successfully flushed {len(orders_to_save)} orders to MySQL and Acked.")

            except Exception as e:
                logger.error(f"Failed to flush orders: {e}")
                # 失败了，将消息回退给 RabbitMQ，让它重新入队
                for msg in messages_to_ack:
                    await msg.nack(requeue=True)
                # 失败后将数据重新放回缓冲区，等待下次重试
                self.buffer.extend(orders_to_save)
                self.message_buffer.extend(messages_to_ack)

    async def on_message(self, message: IncomingMessage):
        """收到消息不立刻 process，先存入内存"""
        try:
            data = json.loads(message.body)
            # 只取需要的字段，节省内存
            async with self.lock:
                self.buffer.append({
                    "user_id": data["user_id"], 
                    "goods_id": data["goods_id"]
                })
                self.message_buffer.append(message)
                
                # 触发落库判断
                should_flush = len(self.buffer) >= 200 or (time.time() - self.last_flush_time) > 0.5
            
            if should_flush:
                # 这里不要用 await，否则会阻塞接收新消息的协程
                # 创建一个后台任务去处理写入
                asyncio.create_task(self.flush_to_db())
        except Exception as e:
            logger.error(f"Error decoding message: {e}")
            await message.nack(requeue=False) # 格式错误的消息直接丢弃

    async def consume(self):
        # 建立连接
        connection = await connect_robust("amqp://guest:guest@localhost/")
        channel = await connection.channel()
        
        # 必须调高 prefetch_count，否则批量写入没意义
        # 建议设为 BATCH_SIZE 的 2-5 倍
        await channel.set_qos(prefetch_count=1000)
        
        queue = await channel.declare_queue(self.queue_name, durable=True)
        
        logger.info("🚀 高性能批量消费者已启动...")
        
        # 核心修改：设置 no_ack=False，表示我们要手动确认
        await queue.consume(self.on_message, no_ack=False)

        try:
            await asyncio.Future()
        finally:
            await connection.close()

if __name__ == "__main__":
    consumer = OrderConsumer()
    try:
        asyncio.run(consumer.consume())
    except KeyboardInterrupt:
        pass