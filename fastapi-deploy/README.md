# FastAPI Docker Compose 部署示例

完整链路：连接池调优 → Redis 缓存 → 缓存预热 → Docker Compose 部署

## 快速开始

```bash
# 1. 进入项目目录
cd fastapi-deploy

# 2. 开发环境启动
docker-compose up --build

# 3. 生产环境后台运行
ENV=prod docker-compose up -d --build
```

## 服务架构

| 服务 | 端口 | 说明 |
|------|------|------|
| web (FastAPI) | 8000 | 主应用接口 |
| worker (Celery) | - | 异步任务消费者 |
| beat (Celery) | - | 定时任务调度 |
| flower | 5555 | Celery 监控面板 |
| redis | 6379 | 缓存 + 消息队列 |
| postgres | 5432 | 数据库 |

## 验证清单

- [ ] `curl http://localhost:8000/health` → `{"status":"ok"}`
- [ ] `curl http://localhost:8000/users` → 用户数据
- [ ] 访问 http://localhost:5555 查看 Flower 面板
- [ ] `docker-compose ps` 所有服务状态为 `Up (healthy)`

## 生产优化

```bash
# 多 worker 扩容
docker-compose up -d --scale worker=3

# 查看日志
docker-compose logs -f web
```

## 环境变量

| 变量 | 开发默认值 | 生产建议 |
|------|-----------|---------|
| DATABASE_URL | postgresql+asyncpg://dev:dev@postgres/devdb | 使用强密码 |
| REDIS_URL | redis://redis:6379/0 | 同左 |
| CELERY_BROKER_URL | redis://redis:6379/1 | 同左 |
| DEBUG | true | false |

⚠️ `.env.prod` 已加入 `.gitignore`，生产密码走 CI/CD Secrets 注入。

## 关联文章

- [Redis 缓存让 QPS 翻倍](https://github.com/hope-999/fastapi-example/tree/main/fastapi-redis-cache)
- [缓存预热 + 异步队列](https://github.com/hope-999/fastapi-example/tree/main/fastapi-prewarm)
- [数据库连接池调优](https://github.com/hope-999/fastapi-example/tree/main/fastapi-pool)
