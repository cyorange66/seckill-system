from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base 

class Goods(Base):
    __tablename__ = "goods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    price = Column(Float)
    stock = Column(Integer)