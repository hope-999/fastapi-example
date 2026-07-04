"""
API 路由示例
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cache import cache, invalidate_cache
from tasks import refresh_user_cache

router = APIRouter()


@router.get("/users")
@cache(ttl=300)
async def list_users():
    """获取用户列表（带缓存）"""
    # TODO: 实际应从数据库查询
    return [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]


@router.get("/users/{user_id}")
@cache(ttl=300)
async def get_user(user_id: int):
    """获取单个用户（带缓存）"""
    # TODO: 实际应从数据库查询
    return {"id": user_id, "name": f"User_{user_id}"}


@router.put("/users/{user_id}")
async def update_user(user_id: int, user_data: dict):
    """更新用户（触发缓存刷新）"""
    # TODO: 实际应更新数据库
    
    # 延迟双删：先删缓存 → 更新数据库 → 再删缓存
    await invalidate_cache(f"cache:user:{user_id}")
    await invalidate_cache("cache:list_users:*")
    
    # TODO: 更新数据库
    
    # 触发异步刷新
    refresh_user_cache.delay(user_id)
    
    return {"status": "updated", "user_id": user_id}


@router.get("/config")
@cache(ttl=600)
async def get_config():
    """获取系统配置（带缓存）"""
    return {"version": "1.0", "features": ["cache", "async"]}
