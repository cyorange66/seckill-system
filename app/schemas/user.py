from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

# 定义API请求数据格式