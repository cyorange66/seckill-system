import os  

class Settings:
    # 从环境变量读取，提供默认值以便本地开发
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "mysql+aiomysql://dev:123456@127.0.0.1:3306/seckill"
    )
    REDIS_URL = os.getenv(
        "REDIS_URL", 
        "redis://127.0.0.1:6379/0"
    )
    RABBITMQ_URL = os.getenv(
        "RABBITMQ_URL",
        "amqp://guest:guest@localhost/"
    )

settings = Settings()  