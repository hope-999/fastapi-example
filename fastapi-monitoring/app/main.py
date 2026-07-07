from fastapi import FastAPI
from prometheus_client import Counter, Histogram, Gauge
from starlette_prometheus import metrics, PrometheusMiddleware

app = FastAPI()
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

# 自定义业务指标
cache_hits = Counter("cache_hits_total", "Cache hit count")
cache_misses = Counter("cache_misses_total", "Cache miss count")
order_duration = Histogram(
    "order_processing_seconds",
    "Time spent processing orders",
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)
queue_depth = Gauge("task_queue_depth", "Current task queue size")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    import time
    start = time.time()
    # 模拟订单处理
    result = {"order_id": order_id, "status": "shipped"}
    order_duration.observe(time.time() - start)
    return result


@app.post("/cache/hit")
def record_cache_hit():
    cache_hits.inc()
    return {"cache": "hit"}


@app.post("/cache/miss")
def record_cache_miss():
    cache_misses.inc()
    return {"cache": "miss"}
