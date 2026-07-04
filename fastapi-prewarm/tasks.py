"""
Celery 任务：缓存预热 + 定时刷新
"""
from celery import shared_task
import redis.asyncio as redis
import json

from main import celery_app, cache_pool


@shared_task(bind=True, max_retries=3)
def prewarm_cache(self):
    """启动时异步预热缓存"""
    import asyncio
    asyncio.run(_prewarm())


async def _prewarm():
    """预热热点数据到 Redis"""
    r = redis.Redis(connection_pool=cache_pool)
    
    # 分布式锁：防止多个 worker 同时预热
    lock = await r.set("lock:prewarm", "1", nx=True, ex=60)
    if not lock:
        return "another worker is prewarming"
    
    try:
        # TODO: 根据实际业务查询数据库并写入缓存
        # 示例：预热配置数据
        config_data = {"version": "1.0", "features": ["cache", "async"]}
        await r.setex("cache:config", 300, json.dumps(config_data))
        
        # 示例：预热用户列表（实际应从数据库查询）
        users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        await r.setex("cache:list_users", 300, json.dumps(users))
        
        return "prewarm done"
    finally:
        await r.delete("lock:prewarm")


@shared_task
def refresh_users():
    """定时刷新用户缓存"""
    import asyncio
    asyncio.run(_refresh_users())


async def _refresh_users():
    r = redis.Redis(connection_pool=cache_pool)
    # TODO: 从数据库查询最新用户数据
    users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    await r.setex("cache:list_users", 300, json.dumps(users))


@shared_task
def refresh_categories():
    """定时刷新分类缓存"""
    import asyncio
    asyncio.run(_refresh_categories())


async def _refresh_categories():
    r = redis.Redis(connection_pool=cache_pool)
    # TODO: 从数据库查询最新分类数据
    categories = [{"id": 1, "name": "Tech"}, {"id": 2, "name": "Life"}]
    await r.setex("cache:categories", 3600, json.dumps(categories))


@shared_task
def refresh_user_cache(user_id: int):
    """事件触发：单个用户缓存刷新"""
    import asyncio
    asyncio.run(_refresh_user(user_id))


async def _refresh_user(user_id: int):
    r = redis.Redis(connection_pool=cache_pool)
    # TODO: 从数据库查询单个用户
    user = {"id": user_id, "name": f"User_{user_id}"}
    await r.setex(f"cache:user:{user_id}", 300, json.dumps(user))
