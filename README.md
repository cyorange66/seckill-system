\# High Concurrency Seckill System



基于 FastAPI + Redis + RabbitMQ + MySQL 实现的高并发秒杀系统。



\## Tech Stack



FastAPI  

Redis  

RabbitMQ  

MySQL  

Lua  

JMeter  



\## Features



\- Redis Lua脚本库存原子扣减

\- RabbitMQ订单异步处理

\- 消息队列削峰

\- MySQL订单存储

\- JMeter高并发压测



\## Stress Test



5000 concurrent requests  

No oversell  

System stable

