from fastapi import APIRouter, HTTPException
from app.core.redis_client import redis_client
from app.core.rabbitmq import mq_manager
import logging

# 初始化路由
router = APIRouter(prefix="/seckill")

# 配置简单的日志，方便观察（生产环境建议调高级别到 WARNING）
logger = logging.getLogger(__name__)

# 1. 在模块加载时预读 Lua 脚本内容
# 这样脚本内容驻留在内存中，每次调用时直接发送给 Redis，速度极快
LUA_SCRIPT_PATH = "app/lua/seckill.lua"
try:
    with open(LUA_SCRIPT_PATH, "r", encoding="utf-8") as f:
        SECKILL_LUA_CONTENT = f.read()
except FileNotFoundError:
    logger.error(f"Lua script not found at {LUA_SCRIPT_PATH}")
    SECKILL_LUA_CONTENT = ""

@router.post("/{goods_id}")
async def seckill(goods_id: int, user_id: int):
    """
    秒杀核心接口：Redis 原子扣减 + MQ 异步削峰
    """
    if not SECKILL_LUA_CONTENT:
        raise HTTPException(status_code=500, detail="Seckill logic not initialized")

    stock_key = f"seckill:stock:{goods_id}"
    user_key = f"seckill:users:{goods_id}"

    try:
        # 2. 异步执行 Lua 脚本 (原子操作)
        # 参数说明: 脚本内容, KEYS数量, KEYS[1], KEYS[2], ARGV[1]
        result = await redis_client.eval(
            SECKILL_LUA_CONTENT, 
            2, 
            stock_key, 
            user_key, 
            user_id
        )

        # 3. 根据 Lua 返回值进行逻辑判断
        # -1: 库存不足
        # -2: 重复购买
        #  >0: 剩余库存数量
        if result == -1:
            return {"code": 400, "msg": "sold out", "data": None}
        
        if result == -2:
            return {"code": 400, "msg": "already bought", "data": None}

        # 4. 只有 Redis 扣减成功，才异步发送 MQ 消息入队
        # 这里的 await 不会阻塞，它会挂起当前协程去处理网络IO，CPU立刻去接待下一个用户请求
        order_data = {
            "user_id": user_id,
            "goods_id": goods_id,
            "status": "pending"
        }
        
        await mq_manager.send_order_message(order_data)

        # 5. 返回抢购成功（实际上是排队中）
        return {
            "code": 200, 
            "msg": "seckill success", 
            "data": {
                "stock_left": result
            }
        }

    except Exception as e:
        # 捕获 Redis 或 MQ 可能抛出的连接异常
        logger.error(f"Seckill Error: {str(e)}")
        return {"code": 500, "msg": "Server Busy, try again later"}