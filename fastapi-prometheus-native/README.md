# FastAPI + Prometheus 官方原生 Python 客户端监控体系

基于 Prometheus 官方 `prometheus-client` 库的原生 FastAPI 监控方案，完全透明可控，支持单进程和多进程（Gunicorn）部署。

## 文章

[服务崩了还没报警？Prometheus 官方 Python 客户端 + FastAPI 5 分钟搭好监控体系](https://mp.weixin.qq.com/s/...)

## 项目结构

```
fastapi-prometheus-native/
├── app/
│   ├── main.py          # 单进程版本（uvicorn 直接启动）
│   └── main_mp.py       # 多进程版本（Gunicorn + 指标聚合）
├── gunicorn.conf.py     # Gunicorn 多进程配置（含 mark_process_dead）
├── prometheus.yml       # Prometheus 抓取配置
├── requirements.txt     # 依赖列表
└── README.md            # 本文件
```

## 快速开始

### 单进程模式（开发/测试）

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

访问 http://localhost:8000/metrics 查看指标。

### 多进程模式（生产）

```bash
export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc
pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py app.main_mp:app
```

## 核心设计

- **手写 Middleware**：完全可控，不依赖黑盒第三方库
- **四种指标类型**：Counter / Gauge / Histogram / Summary，按需选用
- **自定义业务指标**：用户注册漏斗 `user_signup_total` 示例
- **多进程聚合**：`MultiProcessCollector` + `mark_process_dead` 解决数据残留

## 监控链路

FastAPI → Middleware → Prometheus → Grafana

## 关键 PromQL

- QPS：`rate(http_requests_total[1m])`
- P95 延迟：`histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint))`
- 错误率：`sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))`

## 安全提示

`/metrics` 不要暴露到公网。建议：
1. 用 Nginx 加 basic auth
2. 限制内网 IP 访问
3. 或另开一个只监听 127.0.0.1 的 metrics 服务

## License

MIT
