import os  

class Settings:
    DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/seckill_db"
    REDIS_URL = "redis://localhost:6379/0"

settings = Settings()  