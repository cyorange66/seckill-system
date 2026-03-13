local stock_key = KEYS[1]
local user_key = KEYS[2]
local user_id = ARGV[1]

-- 判断库存
local stock = tonumber(redis.call("GET", stock_key))

if not stock or stock <= 0 then
    return -1
end

-- 判断用户是否抢过
if redis.call("SISMEMBER", user_key, user_id) == 1 then
    return -2
end

-- 扣库存
local new_stock = redis.call("DECR", stock_key)

-- 记录用户
redis.call("SADD", user_key, user_id)

return new_stock