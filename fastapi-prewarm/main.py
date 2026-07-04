"""
FastAPI + Redis 缓存预热 + Celery 异步队列
完整示例项目
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
import redis.asyncio as redis
from celery import Celery

# 数据库引擎（连接池已调优）
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,
)

# Redis 连接池
cache_pool = redis.ConnectionPool(
    host="localhost", port=6379, db=0,
    max_connections=50, decode_responses=True,
)

# Redis 消息队列连接池（Celery broker）
broker_pool = redis.ConnectionPool(
    host="localhost", port=6379, db=1,
    max_connections=50, decode_responses=True,
)

# Celery 应用
celery_app = Celery(
    "app",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/1",
)

# Celery Beat 定时任务配置
celery_app.conf.beat_schedule = {
    "refresh-hot-users": {
        "task": "tasks.refresh_users",
        "schedule": 300.0,  # 每 5 分钟
    },
    "refresh-categories": {
        "task": "tasks.refresh_categories",
        "schedule": 3600.0,  # 每小时
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：触发异步预热（不阻塞）
    from tasks import prewarm_cache
    prewarm_cache.delay()
    yield
    # 关闭：优雅释放连接
    await cache_pool.disconnect()
    await broker_pool.disconnect()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
