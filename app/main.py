from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from app.core.database import engine, Base
from app.core.rabbitmq import mq_manager  # 🚀 导入异步 MQ 管理器
from app.api import user, goods, seckill

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 核心优化点：生命周期管理器 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 【数据库】异步建表
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 2. 【RabbitMQ】启动时预热连接 (核心修复点)
    # 这一步会创建长连接并声明 order_queue，确保请求进来时直接能发消息
    logger.info("Connecting to RabbitMQ and declaring queues...")
    try:
        await mq_manager.connect() 
        logger.info("RabbitMQ connected successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        # 禁止程序继续启动，防止秒杀功能失效
        raise RuntimeError("Cannot start application without RabbitMQ connection") from e

    yield
    
    # --- Shutdown 逻辑 ---
    # 3. 关闭数据库连接池
    await engine.dispose()
    
    # 4. 关闭 RabbitMQ 连接
    if mq_manager._connection:
        await mq_manager._connection.close()
    
    logger.info("System resources cleaned up.")

# 将 lifespan 注入 FastAPI
app = FastAPI(
    title="High-Concurrency Seckill System",
    lifespan=lifespan
)

# 注册路由
app.include_router(user.router)
app.include_router(goods.router)
app.include_router(seckill.router)

@app.get("/")
async def root():
    return {"status": "online", "msg": "Seckill system is ready for 5000 QPS"}