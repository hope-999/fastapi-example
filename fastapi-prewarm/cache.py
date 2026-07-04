"""
缓存装饰器 + 缓存防御（穿透、雪崩、击穿）
"""
import json
import hashlib
import random
import asyncio
from functools import wraps
from typing import Any, Optional

import redis.asyncio as redis

# 使用 main.py 中定义的 cache_pool
from main import cache_pool


def cache(ttl: int = 300):
    """缓存装饰器，支持防穿透、防雪崩、防击穿"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存 key
            kwargs_str = str(sorted(kwargs.items()))
            cache_key = f"cache:{func.__name__}:{hashlib.md5(kwargs_str.encode()).hexdigest()[:8]}"
            
            r = redis.Redis(connection_pool=cache_pool)
            
            # 1. 检查缓存
            cached = await r.get(cache_key)
            if cached == "__none__":
                return None
            if cached:
                return json.loads(cached)
            
            # 2. 防击穿：互斥锁
            lock = await r.set(f"lock:{cache_key}", "1", nx=True, ex=10)
            if not lock:
                # 没抢到锁，等待后重试
                await asyncio.sleep(0.1)
                return await wrapper(*args, **kwargs)
            
            try:
                # 3. 执行函数
                result = await func(*args, **kwargs)
                
                # 4. 写入缓存（防穿透：空值缓存）
                actual_ttl = ttl + random.randint(0, 60)  # 防雪崩：随机偏移
                if result is None:
                    await r.setex(cache_key, 60, "__none__")  # 空值缓存 60 秒
                else:
                    await r.setex(cache_key, actual_ttl, json.dumps(result))
                
                return result
            finally:
                # 释放锁
                await r.delete(f"lock:{cache_key}")
        
        return wrapper
    return decorator


async def invalidate_cache(pattern: str):
    """按 pattern 批量删除缓存"""
    r = redis.Redis(connection_pool=cache_pool)
    keys = []
    async for key in r.scan_iter(match=pattern):
        keys.append(key)
    if keys:
        await r.delete(*keys)
