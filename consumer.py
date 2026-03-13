import pika
import json
from app.core.database import SessionLocal
from app.models.order import Order

# 连接 RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        heartbeat=600,
        blocked_connection_timeout=300
    )
)

channel = connection.channel()

# 声明队列
channel.queue_declare(queue="order_queue", durable=True)

# 限制消费者一次只拿10条消息
channel.basic_qos(prefetch_count=10)


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)

        db = SessionLocal()

        order = Order(
            user_id=data["user_id"],
            goods_id=data["goods_id"]
        )

        db.add(order)
        db.commit()
        db.close()

        print("订单创建成功:", data)

        # 手动确认消息
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("订单创建失败:", e)
        # 拒绝消息并丢弃
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


channel.basic_consume(
    queue="order_queue",
    on_message_callback=callback
)

print("等待订单消息...")

channel.start_consuming()