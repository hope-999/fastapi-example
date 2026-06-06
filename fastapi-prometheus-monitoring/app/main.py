from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import random

app = FastAPI(title="FastAPI Prometheus Monitoring Demo")

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0]
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['endpoint', 'status']
)


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    # Skip /metrics endpoint to avoid recursive monitoring
    if request.url.path == '/metrics':
        return await call_next(request)
    
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=str(response.status_code)
    ).inc()
    
    REQUEST_DURATION.labels(
        endpoint=request.url.path
    ).observe(duration)
    
    if response.status_code >= 400:
        ERROR_COUNT.labels(
            endpoint=request.url.path,
            status=str(response.status_code)
        ).inc()
    
    return response


@app.get("/")
async def root():
    return {"message": "FastAPI Prometheus Monitoring Demo"}


@app.get("/items")
async def read_items():
    # Simulate random delay
    await simulate_delay(0.01, 0.1)
    return [{"name": "Foo"}, {"name": "Bar"}]


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    await simulate_delay(0.01, 0.2)
    return {"item_id": item_id, "name": f"Item {item_id}"}


@app.get("/slow")
async def slow_endpoint():
    # Simulate a slow operation (0.5-2s)
    await simulate_delay(0.5, 2.0)
    return {"done": True, "duration": "slow"}


@app.get("/error")
async def error_endpoint():
    # Simulate occasional errors (30% chance)
    if random.random() < 0.3:
        raise HTTPException(status_code=500, detail="Simulated error")
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/health")
async def health():
    return {"status": "healthy"}


async def simulate_delay(min_sec: float, max_sec: float):
    """Simulate async IO delay"""
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)


from fastapi import HTTPException
import asyncio

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
