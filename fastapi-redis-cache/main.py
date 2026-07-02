from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Field, select
import redis.asyncio as redis
import json
import hashlib
import random
import asyncio
from contextlib import asynccontextmanager

# ============================================================
# 数据库连接池（生产环境配置）
# ============================================================
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,
    echo=False,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ============================================================
# Redis 连接池
# ============================================================
redis_pool = redis.ConnectionPool(
    host="localhost", port=6379, db=0,
    max_connections=50, decode_responses=True
)


# ============================================================
# 缓存装饰器（含防御策略）
# ============================================================
def cache(ttl: int = 300):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            r = await redis.Redis(connection_pool=redis_pool)
            cache_key = f"cache:{func.__name__}:{hashlib.md5(str(kwargs).encode()).hexdigest()[:8]}"
            actual_ttl = ttl + random.randint(0, 60)  # 防雪崩：TTL随机偏移
            
            cached = await r.get(cache_key)
            if cached == "__none__":
                return None
            if cached and cached != "__lock__":
                return json.loads(cached)
            
            # 防击穿：互斥锁
            lock = await r.set(cache_key, "__lock__", nx=True, ex=10)
            if not lock:
                await asyncio.sleep(0.1)
                return await wrapper(*args, **kwargs)
            
            result = await func(*args, **kwargs)
            if result is None:
                await r.setex(cache_key, 60, "__none__")  # 防穿透：空值缓存
            else:
                await r.setex(cache_key, actual_ttl, json.dumps(result))
            return result
        return wrapper
    return decorator


# ============================================================
# 模型定义
# ============================================================
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str


# ============================================================
# 路由
# ============================================================
router = APIRouter()

@router.get("/users")
@cache(ttl=300)
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return [u.model_dump() for u in result.scalars().all()]


@router.get("/users/{user_id}")
@cache(ttl=300)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user.model_dump() if user else None


@router.put("/users/{user_id}")
async def update_user(user_id: int, name: str, email: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import update
    await db.execute(update(User).where(User.id == user_id).values(name=name, email=email))
    await db.commit()
    
    # 缓存失效：删除相关缓存
    r = await redis.Redis(connection_pool=redis_pool)
    await r.delete(f"cache:get_user:*")
    pattern = "cache:list_users:*"
    async for key in r.scan_iter(match=pattern):
        await r.delete(key)
    
    return {"status": "updated"}


# ============================================================
# 应用入口
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_pool.disconnect()

app = FastAPI(title="FastAPI Redis Cache Demo", lifespan=lifespan)
app.include_router(router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
