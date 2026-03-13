from fastapi import APIRouter
from app.core.redis_client import redis_client
from app.core.rabbitmq import send_order_message

router = APIRouter(prefix="/seckill")

print("SECKILL FILE LOADED")

# 读取 Lua 脚本
with open("app/lua/seckill.lua", "r", encoding="utf-8") as f:
    lua_script = f.read()

seckill_lua = redis_client.register_script(lua_script)


@router.post("/{goods_id}")
def seckill(goods_id: int, user_id: int):

    stock_key = f"seckill:stock:{goods_id}"
    user_key = f"seckill:users:{goods_id}"

    result = seckill_lua(keys=[stock_key, user_key], args=[user_id])

    if result == -1:
        return {"msg": "sold out"}

    if result == -2:
        return {"msg": "already bought"}

    # 只有成功才发送 MQ
    print(f"Sending message for user {user_id} and goods {goods_id}")

    send_order_message({
        "user_id": user_id,
        "goods_id": goods_id
    })

    return {
        "msg": "seckill success",
        "stock_left": result
    }