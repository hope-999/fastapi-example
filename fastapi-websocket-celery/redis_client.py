# redis_client.py
import json
import redis.asyncio as redis
from contextlib import asynccontextmanager

# Redis 配置集中管理
REDIS_URL = "redis://localhost:6379/0"

class RedisClient:
    """Redis 客户端封装，支持 Pub/Sub"""
    
    def __init__(self, url: str = REDIS_URL):
        self.url = url
        self._client: redis.Redis | None = None
    
    async def connect(self):
        """建立连接"""
        self._client = redis.from_url(self.url, decode_responses=True)
    
    async def disconnect(self):
        """断开连接"""
        if self._client:
            await self._client.close()
    
    async def publish(self, channel: str, message: dict):
        """发布消息到指定频道"""
        if not self._client:
            raise RuntimeError("Redis not connected")
        await self._client.publish(channel, json.dumps(message))
    
    @asynccontextmanager
    async def subscribe(self, channel: str):
        """订阅频道（上下文管理器，自动清理）"""
        if not self._client:
            raise RuntimeError("Redis not connected")
        
        pubsub = self._client.pubsub()
        await pubsub.subscribe(channel)
        try:
            yield pubsub
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()

# 全局实例
redis_client = RedisClient()
