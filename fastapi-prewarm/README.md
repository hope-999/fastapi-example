# FastAPI 缓存预热 + 异步队列

完整示例项目，对应公众号文章《Redis 刚启动就挨揍？缓存预热 + 异步队列 5 分钟让第一个用户不再等》。

## 架构

```
Nginx → FastAPI → Redis（缓存）→ PostgreSQL
              ↓
         Celery Worker（预热/刷新任务）
              ↓
         Redis（消息队列 db1）
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动 Redis

```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

### 3. 启动 Celery Worker

```bash
celery -A tasks worker --loglevel=info
```

### 4. 启动 Celery Beat（定时任务）

```bash
celery -A tasks beat --loglevel=info
```

### 5. 启动 FastAPI

```bash
uvicorn main:app --reload
```

## 核心特性

- **连接池调优**：PostgreSQL pool_size=20, max_overflow=10
- **Redis 缓存**：命中 QPS 5620，P99 18ms
- **缓存防御**：防穿透（空值缓存）、防雪崩（TTL 随机偏移）、防击穿（互斥锁）
- **异步预热**：Celery 后台预热，不阻塞启动
- **定时刷新**：Celery Beat 每 5 分钟刷新热点数据
- **事件触发**：数据变更时异步更新缓存

## 项目结构

```
.
├── main.py          # FastAPI 应用 + 生命周期管理
├── cache.py         # 缓存装饰器 + 防御机制
├── tasks.py         # Celery 任务（预热 + 刷新）
├── routes.py        # API 路由示例
└── requirements.txt # 依赖
```

## 监控指标

| 指标 | 正常范围 | 告警阈值 |
|------|----------|----------|
| 预热完成时间 | < 30s | > 60s |
| 缓存命中率 | > 85% | < 70% |
| 预热期间数据库 CPU | < 30% | > 50% |
| 定时任务延迟 | < 10s | > 60s |

## 文章链接

- [FastAPI 数据库连接池炸了？生产环境 502 的元凶找到了](#)
- [重复查询把数据库打崩了？Redis 缓存 5 分钟让 QPS 翻倍](#)
- [Redis 刚启动就挨揍？缓存预热 + 异步队列 5 分钟让第一个用户不再等](#)

## License

MIT
