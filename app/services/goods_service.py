from sqlalchemy.orm import Session
from app.models.goods import Goods
from app.services.redis_service import set_stock

def create_goods(db: Session, name: str, price: float, stock: int):
    goods = Goods(
        name=name,
        price=price,
        stock=stock
    )

    db.add(goods)
    db.commit()
    db.refresh(goods)

    # 把库存写入 Redis
    set_stock(goods.id, stock)

    return goods