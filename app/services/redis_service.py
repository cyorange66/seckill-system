from app.core.redis_client import redis_client

def set_stock(goods_id: int, stock: int):
    key = f"seckill:stock:{goods_id}"
    redis_client.set(key, stock)

def get_stock(goods_id: int):
    key = f"seckill:stock:{goods_id}"
    return redis_client.get(key)