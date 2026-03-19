from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# 🚀 2. 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,              # 压测时务必设为 False，避免打印 SQL 带来的 IO 损耗
    pool_size=100,           # 连接池基础大小，5000 QPS 建议设为 100 左右
    max_overflow=50,         # 允许临时溢出的连接数
    pool_recycle=3600,       # 自动回收 1 小时前的连接，防止断开
    pool_pre_ping=True       # 每次取连接前先检测是否可用，防止 "MySQL Server has gone away"
)

# 注意这里使用 async_sessionmaker 和 AsyncSession
async_session_local = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # 异步环境下建议设为 False，防止对象被销毁后无法读取属性
)

Base = declarative_base()

SessionLocal = async_session_local

async def get_db():
    async with async_session_local() as session:
        try:
            yield session
        finally:
            await session.close()