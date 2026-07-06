"""FastAPI + Docker Compose 部署示例

完整链路：连接池 → Redis 缓存 → 缓存预热 → Docker Compose 部署
"""

import json
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from config import settings, engine, redis_pool

# Celery 应用（从 tasks 导入，避免循环引用）
from tasks import celery_app, prewarm_cache

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_redis():
    r = redis.Redis(connection_pool=redis_pool)
    try:
        yield r
    finally:
        await r.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：触发异步预热（不阻塞）
    prewarm_cache.delay()
    yield
    # 关闭：优雅释放连接
    await redis_pool.disconnect()
    await engine.dispose()


app = FastAPI(title="FastAPI Deploy Demo", lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/users")
async def list_users(r: redis.Redis = Depends(get_redis), db: AsyncSession = Depends(get_db)):
    # 先查缓存
    cached = await r.get("cache:list_users")
    if cached:
        return {"source": "cache", "data": json.loads(cached)}

    # 缓存未命中，查数据库
    result = await db.execute(text("SELECT id, name, email FROM users LIMIT 100"))
    rows = [dict(row._mapping) for row in result.fetchall()]

    # 写入缓存
    await r.setex("cache:list_users", 300, json.dumps(rows))
    return {"source": "db", "data": rows}


@app.get("/users/{user_id}")
async def get_user(user_id: int, r: redis.Redis = Depends(get_redis), db: AsyncSession = Depends(get_db)):
    cache_key = f"cache:user:{user_id}"
    cached = await r.get(cache_key)
    if cached:
        return {"source": "cache", "data": json.loads(cached)}

    result = await db.execute(text("SELECT id, name, email FROM users WHERE id = :uid").bindparams(uid=user_id))
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    data = dict(row._mapping)
    await r.setex(cache_key, 300, json.dumps(data))
    return {"source": "db", "data": data}
