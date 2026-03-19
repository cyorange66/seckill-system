from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.goods import Goods
from app.schemas.goods import GoodsCreate
from app.services.goods_service import create_goods as create_goods_service

router = APIRouter(prefix="/goods")

@router.get("/list")
async def list_goods(db: AsyncSession = Depends(get_db)): # 🚀 改为 async def
    # 2. 异步查询写法：使用 execute(select(...))
    result = await db.execute(select(Goods))
    goods_list = result.scalars().all()
    return goods_list

@router.post("/create")
async def create_goods(goods: GoodsCreate, db: AsyncSession = Depends(get_db)):
    # 3. 这里的 service 层也必须是异步的
    # 如果你的 create_goods_service 还没改异步，这里会报错
    new_goods = await create_goods_service(
        db,
        goods.name,
        goods.price,
        goods.stock
    )
    return new_goods