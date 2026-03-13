from fastapi import FastAPI
from app.core.database import engine, Base

# 导入模型（让SQLAlchemy注册表）
import app.models.user
import app.models.goods
import app.models.order

# 导入API路由
from app.api import user, goods, seckill

app = FastAPI()

# 自动建表
Base.metadata.create_all(bind=engine)

# 注册路由
app.include_router(user.router)
app.include_router(goods.router)
app.include_router(seckill.router)


@app.get("/")
def root():
    return {"msg": "seckill system running"}