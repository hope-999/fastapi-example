# FastAPI Redis 缓存 — 生产环境配置示例

对应文章：[重复查询把数据库打崩了？Redis 缓存 5 分钟让 QPS 翻倍](https://mp.weixin.qq.com)

## 核心功能

- **缓存装饰器**：`@cache(ttl=300)` 一键缓存接口返回
- **防御三件套**：
  - 缓存穿透：空值缓存（`__none__`）
  - 缓存雪崩：TTL 随机偏移（+0~60 秒）
  - 缓存击穿：互斥锁（mutex）
- **缓存失效**：更新数据后主动清除相关缓存

## 架构

```
Nginx → FastAPI → Redis → PostgreSQL
```

Redis 挡掉 80% 重复查询，PostgreSQL 只处理写操作和缓存未命中。

## 运行

```bash
# 启动 Redis
docker run -d -p 6379:6379 redis:7-alpine

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload
```

## 测试

```bash
# 首次请求（缓存未命中，查数据库）
curl http://localhost:8000/api/users

# 再次请求（缓存命中，直接返回）
curl http://localhost:8000/api/users

# 更新数据（触发缓存失效）
curl -X PUT "http://localhost:8000/api/users/1?name=Alice&email=alice@example.com"

# 再次请求（缓存已清，重新加载）
curl http://localhost:8000/api/users
```

## 关键配置

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `ttl` | 缓存有效期 | 300 秒 |
| `max_connections` | Redis 连接池 | 50 |
| `pool_size` | 数据库常备连接 | 20 |
| `max_overflow` | 数据库临时连接 | 10 |
