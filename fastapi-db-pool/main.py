from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Field, select
from contextlib import asynccontextmanager
from prometheus_client import Gauge, make_asgi_app

# ============================================================
# 数据库连接池配置 — 生产环境推荐参数
# ============================================================
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # 常备 20 个连接（4 核服务器推荐）
    max_overflow=10,        # 突发流量缓冲
    pool_pre_ping=True,     # 连接健康检查，防僵尸连接
    pool_recycle=3600,      # 1 小时回收
    pool_timeout=30,        # 获取连接超时 30 秒
    echo=False,             # 生产关闭 SQL 日志
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# ============================================================
# Session 依赖（正确关闭，防泄漏）
# ============================================================
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


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
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()


# ============================================================
# 监控指标
# ============================================================
pool_size_gauge = Gauge("db_pool_size", "Database pool size")
pool_checked_out = Gauge("db_pool_checked_out", "Checked out connections")

@router.get("/health")
async def health_check():
    pool = engine.pool
    pool_size_gauge.set(pool.size())
    pool_checked_out.set(pool.checkedout())
    return {
        "status": "ok",
        "pool_size": pool.size(),
        "checked_out": pool.checkedout(),
        "available": pool.checkedin(),
    }


# ============================================================
# 应用入口
# ============================================================
app = FastAPI(title="FastAPI DB Pool Demo")
app.include_router(router, prefix="/api")

# Prometheus 指标端点
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
