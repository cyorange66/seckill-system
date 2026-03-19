from sqlalchemy.ext.asyncio import AsyncSession # 🚀 导入异步 Session 类型
from app.models.user import User

async def create_user(db: AsyncSession, username: str, password: str): # 🚀 改为 async def
    user = User(username=username, password=password)
    
    db.add(user)
    
    # 🚀 所有的数据库 IO 操作都必须加上 await
    await db.commit()   
    await db.refresh(user) 
    
    return user