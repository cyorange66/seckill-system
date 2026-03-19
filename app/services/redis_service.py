from app.core.redis_client import redis_client

async def set_stock(goods_id: int, stock: int):
    """
    异步预热库存到 Redis
    """
    key = f"seckill:stock:{goods_id}"
    # 🚀 必须使用 await，否则数据不会真正写入 Redis
    await redis_client.set(key, stock)

async def get_stock(goods_id: int):
    """
    异步获取 Redis 中的库存
    """
    key = f"seckill:stock:{goods_id}"
    # 🚀 必须使用 await
    return await redis_client.get(key)