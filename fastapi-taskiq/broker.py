from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend
from config import get_settings

# 结果后端（可选，但推荐）
result_backend = RedisAsyncResultBackend(
    "redis://localhost:6379",
    result_ex_time=3600,  # 1 小时后过期
)

# Broker 定义
broker = ListQueueBroker("redis://localhost:6379").with_result_backend(
    result_backend
)
