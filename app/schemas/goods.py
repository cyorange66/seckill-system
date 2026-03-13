from pydantic import BaseModel

class GoodsCreate(BaseModel):
    name: str
    price: float
    stock: int