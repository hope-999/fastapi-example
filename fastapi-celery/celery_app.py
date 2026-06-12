from celery import Celery
from config import BROKER_URL, BACKEND_URL

celery_app = Celery(
    "worker",
    broker=BROKER_URL,
    backend=BACKEND_URL,
    include=["tasks"],  # 必须显式注册任务模块
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    # 结果保留 1 小时，防止 Redis 内存无限增长
    result_expires=3600,
    # 任务默认超时 5 分钟
    task_soft_time_limit=300,
    task_time_limit=360,
)

celery_app.conf.beat_schedule = {
    "cleanup-daily": {
        "task": "tasks.cleanup_old_files",
        "schedule": 86400.0,  # 每 24 小时
    },
}
