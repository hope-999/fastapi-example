from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import asyncio

# ═══════════════════════════════════════════════════════
# 1. 定义指标
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

# 业务指标：用户注册漏斗
SIGNUP_EVENTS = Counter(
    'user_signup_total',
    'User signup events by outcome',
    ['outcome']
)

# Gauge 示例：异步任务队列长度（模拟）
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

    # 过滤 /metrics 和 /health，避免自监控污染数据
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
# 3. 暴露 /metrics 端点（单进程版本）
# ═══════════════════════════════════════════════════════

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
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
    """模拟注册处理逻辑"""
    if "@" not in data.email:
        raise ValidationError("Invalid email")
    await asyncio.sleep(0.01)  # 模拟 DB 操作


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
    await asyncio.sleep(0.02)  # 模拟延迟
    return {"items": [1, 2, 3]}


@app.get("/health")
async def health():
    return {"status": "ok"}


# ═══════════════════════════════════════════════════════
# 5. 模拟队列长度 Gauge 更新任务（仅单进程演示）
# ═══════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_gauge_worker():
    async def gauge_worker():
        # 模拟队列长度变化，生产环境用 redis.llen() 等
        while True:
            QUEUE_LENGTH.set(10 + int(time.time()) % 20)
            await asyncio.sleep(5)

    asyncio.create_task(gauge_worker())
