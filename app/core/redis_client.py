import redis.asyncio as redis
from app.core.config import settings
from urllib.parse import urlparse

# 解析 Redis URL
redis_url = settings.REDIS_URL
parsed_url = urlparse(redis_url)

# 创建异步连接池
pool = redis.ConnectionPool.from_url(
    redis_url,
    decode_responses=True,
    max_connections=200
)

# 创建异步 Redis 客户端实例
redis_client = redis.Redis(connection_pool=pool)