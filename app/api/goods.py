from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.goods import Goods
from app.schemas.goods import GoodsCreate
from app.services.goods_service import create_goods as create_goods_service

router = APIRouter(prefix="/goods")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/list")
def list_goods(db: Session = Depends(get_db)):
    goods_list = db.query(Goods).all()
    return goods_list


@router.post("/create")
def create_goods(goods: GoodsCreate, db: Session = Depends(get_db)):
    new_goods = create_goods_service(
        db,
        goods.name,
        goods.price,
        goods.stock
    )

    return new_goods