# 🚀 高并发异步秒杀系统

本项目是一个基于 FastAPI + Redis + RabbitMQ + MySQL 构建的高性能秒杀系统，核心解决库存超卖与数据库高压问题。

## 🛠️ 技术栈
* **Web**: FastAPI (异步架构)
* **控货**: Redis + Lua (原子扣减)
* **削峰**: RabbitMQ (异步解耦)
* **持久化**: MySQL 8.0 (aiomysql 批量写入)

## ✨ 核心亮点
* **0 超卖**: 采用 Lua 脚本实现 Redis 预减库存，从逻辑根源杜绝超卖。
* **极速响应**: 接入层秒级返回，平均延迟仅 **12.69ms**。
* **吞吐量**: 单机测试吞吐量达到 **1707 QPS**。
* **批量入库**: 消费者支持 200 条/次的批量写入，缓解磁盘 I/O 压力。

## 📈 压测表现 (JMeter 1000 线程)
* **总请求**: 10,000
* **吞吐量**: 1707.94 req/s
* **成功率**: 100% (HTTP OK)
* **数据一致性**: 5000 库存精准扣罄，MySQL 成功入库 4976 条 (99.5% 转化率)。
* **压测结果**：见docs/images。

## 📂 项目结构
* `app/api/`: 秒杀业务逻辑
* `app/core/`: 数据库、MQ、Redis 连接池
* `app/lua/`: 原子扣减脚本
* `consumer.py`: 高性能批量消费者

## 🚀 快速启动
1. `pip install -r requirements.txt`
2. `redis-cli set seckill:stock:17 5000`
3. 启动 Web: `uvicorn app.main:app`
4. 启动 Worker: `python consumer.py`