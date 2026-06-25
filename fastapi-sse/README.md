# FastAPI SSE 实战示例

> WebSocket 太重了，SSE 刚刚好。

本项目演示如何在 FastAPI 中使用 Server-Sent Events (SSE) 实现轻量级实时推送，包含基础示例和 AI 打字机效果。

---

## 目录

- `main.py` — SSE 基础示例（定时推送消息）
- `chat_app.py` — AI 打字机效果（流式调用 LLM API）
- `nginx.conf` — 生产环境 Nginx 反向代理配置
- `docker-compose.yml` — 一键部署模板

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行基础示例

```bash
uvicorn main:app --reload
```

访问 `http://localhost:8000/stream`，浏览器会自动建立 SSE 连接，每秒收到一条消息。

### 3. 运行 AI 打字机示例

配置 LLM API Key：

```bash
export OPENAI_API_KEY="your-key"
# 或写入 .env 文件
```

```bash
uvicorn chat_app:app --reload
```

前端访问 `http://localhost:8000` 即可体验逐字输出效果。

---

## 生产环境部署

### Nginx 反向代理（关键配置）

```nginx
location /stream {
    proxy_pass http://fastapi_backend;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    
    proxy_buffering off;   # ⚠️ 必须关闭缓冲！
    proxy_cache off;       # 关闭缓存
    
    proxy_read_timeout 3600s;  # 长连接超时
}
```

### Docker 部署

```bash
docker-compose up -d
```

---

## 核心要点

| 要点 | 说明 |
|------|------|
| 协议 | HTTP 原生，无需额外库 |
| 自动重连 | 浏览器内置（默认 3 秒） |
| 前端代码 | `new EventSource('/stream')` |
| 关键配置 | `media_type="text/event-stream"` |
| 生产陷阱 | 忘记关闭 Nginx `proxy_buffering` |

---

## 系列文章

- [FastAPI 日志持久化](https://github.com/hope-999/fastapi-example/tree/main/fastapi-log-persistence)
- [FastAPI 性能监控](https://github.com/hope-999/fastapi-example/tree/main/fastapi-prometheus-monitoring)
- [FastAPI 部署指南](https://github.com/hope-999/fastapi-example/tree/main/fastapi-deploy-prod)
- [FastAPI + Celery](https://github.com/hope-999/fastapi-example/tree/main/fastapi-celery)
- [FastAPI + WebSocket + Celery](https://github.com/hope-999/fastapi-example/tree/main/fastapi-websocket-celery)
- [FastAPI + arq](https://github.com/hope-999/fastapi-example/tree/main/fastapi-arq)
- [FastAPI + Taskiq](https://github.com/hope-999/fastapi-example/tree/main/fastapi-taskiq)
- **FastAPI + SSE（本文）**

---

作者：[洛水之风](https://mp.weixin.qq.com)
