import json
import asyncio
import logging
from aio_pika import connect_robust, Message, DeliveryMode
from aio_pika.abc import AbstractRobustConnection
from app.core.config import settings

logger = logging.getLogger(__name__)

class RabbitMQManager:
    def __init__(self, amqp_url: str = None):
        self.amqp_url = amqp_url or settings.RABBITMQ_URL
        self.amqp_url = amqp_url
        self._connection = None
        self._channel = None

    async def connect(self):
        """在 lifespan 启动时调用，建立长连接和持久 Channel"""
        if not self._connection or self._connection.is_closed:
            try:
                self._connection = await connect_robust(self.amqp_url)
                self._channel = await self._connection.channel()
                # 💡 关键优化：只在启动时声明一次队列，不要在发消息时重复声明
                await self._channel.declare_queue("order_queue", durable=True)
                logger.info("RabbitMQ connection established successfully")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise
        return self._channel

    async def send_order_message(self, data: dict):
        """
        核心方法：复用已经开启的 channel 发送消息
        """
        if not self._channel or self._channel.is_closed:
            await self.connect()

        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        
        try:
            # 直接使用预热好的 _channel 发送，省去了 acquire 池的开销
            await self._channel.default_exchange.publish(
                Message(
                    body=body,
                    delivery_mode=DeliveryMode.PERSISTENT
                ),
                routing_key="order_queue"
            )
            logger.info(f"Order message sent successfully: user_id={data.get('user_id')}, goods_id={data.get('goods_id')}")
        except Exception as e:
            logger.error(f"Failed to send order message: {e}")
            # 如果发送失败，尝试重新连接后重试一次
            await self.connect()
            await self._channel.default_exchange.publish(
                Message(
                    body=body,
                    delivery_mode=DeliveryMode.PERSISTENT
                ),
                routing_key="order_queue"
            )

# 初始化全局单例
mq_manager = RabbitMQManager()