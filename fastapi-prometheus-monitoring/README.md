# FastAPI 性能监控：从日志到 Prometheus 指标

> 日志告诉你"发生了什么"，指标告诉你"发生了多少次"。🔥

## 项目结构

```
fastapi-prometheus-monitoring/
├── app/
│   ├── main.py           # FastAPI 应用 + 中间件自动采集
│   ├── Dockerfile        # 容器化
│   └── requirements.txt  # Python 依赖
├── grafana/
│   └── provisioning/     # Grafana 自动配置
├── docker-compose.yml    # 一键启动三件套
├── prometheus.yml        # Prometheus 采集配置
└── README.md
```

## 快速启动

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd fastapi-prometheus-monitoring

# 2. 一键启动
docker-compose up -d

# 3. 访问服务
# FastAPI 应用: http://localhost:8000
# Prometheus:  http://localhost:9090
# Grafana:     http://localhost:3000 (admin/admin)
# /metrics 端点: http://localhost:8000/metrics
```

## 生成测试数据

```bash
# 压测脚本，生成指标数据
while true; do
  curl -s http://localhost:8000/items > /dev/null
  curl -s http://localhost:8000/slow > /dev/null
  curl -s http://localhost:8000/error > /dev/null || true
  sleep 0.5
done
```

## 核心指标

| 指标名 | 类型 | 说明 |
|--------|------|------|
| `http_requests_total` | Counter | 请求总数，按 method/endpoint/status 分组 |
| `http_request_duration_seconds` | Histogram | 请求延迟分布，自动计算 P50/P90/P99 |
| `http_errors_total` | Counter | 错误总数 |

## 关键配置

### 中间件自动采集（零侵入）

```python
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    if request.url.path == '/metrics':
        return await call_next(request)
    
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    REQUEST_COUNT.labels(...).inc()
    REQUEST_DURATION.labels(...).observe(duration)
    return response
```

### 安全提醒

- **生产环境** `/metrics` 不要暴露到公网
- 用 Nginx 白名单或 Basic Auth 保护
- 默认 Grafana 密码 `admin/admin`，上线后修改

## 相关文章

- [FastAPI 日志持久化：为什么你的日志总在服务器重启后消失](link)
- 下一篇：《分布式追踪：用一个 Trace ID 串联全链路请求》

---

作者：洛水之风 | 专注后端工程化与云原生实践
