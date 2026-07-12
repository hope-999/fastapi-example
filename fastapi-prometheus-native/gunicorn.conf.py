import os
from prometheus_client import multiprocess

# ═══════════════════════════════════════════════════════
# Gunicorn 多进程配置
# 必须配置 mark_process_dead，否则 worker 重启后数据残留
# ═══════════════════════════════════════════════════════

prometheus_multiproc_dir = "/tmp/prometheus_multiproc"
os.makedirs(prometheus_multiproc_dir, exist_ok=True)


def child_exit(server, worker):
    """
    worker 退出时标记为死亡，清理旧指标文件。
    不配置这行，僵尸进程的指标会永远残留，导致数据虚高。
    """
    multiprocess.mark_process_dead(worker.pid)


# 可选：自定义 gunicorn 配置
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 60
