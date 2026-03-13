import json

import pika

_connection = None
_channel = None


def _get_channel() -> pika.adapters.blocking_connection.BlockingChannel:
    """
    懒加载 RabbitMQ 连接/通道，适配 uvicorn --reload 多进程场景。
    """
    global _connection, _channel

    if _connection is None or _connection.is_closed:
        _connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        _channel = _connection.channel()
        # 与 consumer.py 中的声明保持一致（durable 默认 False）
        _channel.queue_declare(queue="order_queue", durable=True)

    return _channel


def send_order_message(data: dict) -> None:
    """
    发送订单消息到 RabbitMQ 的 order_queue。
    """
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")

    ch = _get_channel()
    try:
        ch.basic_publish(exchange="", routing_key="order_queue", body=body)
        print("MQ发送成功:", data)
    except Exception as exc:
        # 出现异常时尝试重连一次
        global _connection, _channel
        print("MQ发送失败，准备重连:", exc)
        _connection = None
        _channel = None
        ch = _get_channel()
        ch.basic_publish(exchange="", routing_key="order_queue", body=body)
        print("MQ重新发送成功:", data)