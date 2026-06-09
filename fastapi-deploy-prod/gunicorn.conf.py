import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

graceful_timeout = 30
timeout = 60
keepalive = 2

accesslog = "-"
errorlog = "-"
loglevel = "info"


def on_starting(server):
    pass


def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")
