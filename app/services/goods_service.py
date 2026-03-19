from sqlalchemy.ext.asyncio import AsyncSession
from app.models.goods import Goods
from app.services.redis_service import set_stock # 🚀 确保这个函数也是 async 的

async def create_goods(db: AsyncSession, name: str, price: float, stock: int):
    # 1. 创建模型对象 (同步操作，不涉及 IO)
    goods = Goods(
        name=name,
        price=price,
        stock=stock
    )

    # 2. 异步写入 MySQL
    db.add(goods)
    await db.commit()      # 🚀 必须 await
    await db.refresh(goods) # 🚀 必须 await

    # 3. 异步同步到 Redis
    # 这样秒杀开始时，Redis 里就已经有初始库存了
    await set_stock(goods.id, stock) # 🚀 必须 await

    return goods