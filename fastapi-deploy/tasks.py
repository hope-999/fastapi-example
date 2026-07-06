"""Celery 任务模块

分离 Celery 配置，避免循环导入。
"""

import json
import asyncio

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import redis.asyncio as redis

from config import settings, engine, redis_pool

# Celery 实例
celery_app = Celery(
    "app",
    broker=settings.celery_broker_url,
    backend=settings.celery_broker_url,
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task
def prewarm_cache():
    """缓存预热任务"""
    asyncio.run(_async_prewarm())
    return "prewarm done"


async def _async_prewarm():
    r = redis.Redis(connection_pool=redis_pool)
    db = AsyncSessionLocal()
    try:
        result = await db.execute(text("SELECT id, name, email FROM users LIMIT 1000"))
        rows = [dict(row._mapping) for row in result.fetchall()]
        await r.setex("cache:list_users", 300, json.dumps(rows))
        print(f"Prewarmed {len(rows)} users")
    except Exception as e:
        print(f"Prewarm failed: {e}")
    finally:
        await db.close()
        await r.close()


@celery_app.task
def refresh_user_cache(user_id: int):
    """单个用户缓存刷新"""
    asyncio.run(_async_refresh_user(user_id))
    return f"refreshed user {user_id}"


async def _async_refresh_user(user_id: int):
    r = redis.Redis(connection_pool=redis_pool)
    db = AsyncSessionLocal()
    try:
        result = await db.execute(
            text("SELECT id, name, email FROM users WHERE id = :uid").bindparams(uid=user_id)
        )
        row = result.fetchone()
        if row:
            data = dict(row._mapping)
            await r.setex(f"cache:user:{user_id}", 300, json.dumps(data))
    finally:
        await db.close()
        await r.close()


# Beat 定时调度
celery_app.conf.beat_schedule = {
    "refresh-hot-users": {
        "task": "tasks.prewarm_cache",
        "schedule": 300.0,  # 每 5 分钟
    },
}
celery_app.conf.timezone = "UTC"
