"""
多进程部署适配版 main.py

用法：
    PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc \
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py main_mp:app
"""

import os
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from prometheus_client import (
    Counter, Histogram, Gauge,
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, multiprocess
)
import time
import asyncio


# ═══════════════════════════════════════════════════════
# 1. 定义指标（多进程模式下使用环境变量目录）
# ═══════════════════════════════════════════════════════

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

SIGNUP_EVENTS = Counter(
    'user_signup_total',
    'User signup events by outcome',
    ['outcome']
)

QUEUE_LENGTH = Gauge('task_queue_length', 'Current task queue length')


# ═══════════════════════════════════════════════════════
# 2. 创建应用 & 注册中间件
# ═══════════════════════════════════════════════════════

app = FastAPI()

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    if request.url.path not in ('/metrics', '/health'):
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        REQUEST_DURATION.labels(
            endpoint=request.url.path
        ).observe(duration)

    return response


# ═══════════════════════════════════════════════════════
# 3. 暴露 /metrics 端点（多进程聚合版）
# ═══════════════════════════════════════════════════════

@app.get("/metrics")
async def metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )


# ═══════════════════════════════════════════════════════
# 4. 业务路由
# ═══════════════════════════════════════════════════════

class SignupData(BaseModel):
    email: str
    password: str


class ValidationError(Exception):
    pass


async def process_signup(data: SignupData) -> None:
    if "@" not in data.email:
        raise ValidationError("Invalid email")
    await asyncio.sleep(0.01)


@app.post("/signup")
async def signup(data: SignupData):
    try:
        await process_signup(data)
        SIGNUP_EVENTS.labels(outcome='success').inc()
        return {"ok": True}
    except ValidationError:
        SIGNUP_EVENTS.labels(outcome='invalid').inc()
        return {"ok": False, "reason": "invalid"}
    except Exception:
        SIGNUP_EVENTS.labels(outcome='error').inc()
        raise


@app.get("/items")
async def get_items():
    await asyncio.sleep(0.02)
    return {"items": [1, 2, 3]}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.on_event("startup")
async def startup_gauge_worker():
    async def gauge_worker():
        while True:
            QUEUE_LENGTH.set(10 + int(time.time()) % 20)
            await asyncio.sleep(5)

    asyncio.create_task(gauge_worker())
