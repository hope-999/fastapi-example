"""共享配置模块

避免 main.py 和 tasks.py 之间循环导入。
"""

from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine
import redis.asyncio as redis


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://dev:dev@localhost/devdb"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()

# 数据库引擎（连接池已调优）
engine = create_async_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Redis 连接池
redis_pool = redis.ConnectionPool.from_url(
    settings.redis_url, max_connections=50, decode_responses=True
)
