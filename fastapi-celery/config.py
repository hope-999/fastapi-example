import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
# 分开两个库，避免队列和结果互相干扰
BROKER_URL = REDIS_URL + "?db=0"
BACKEND_URL = REDIS_URL + "?db=1"
