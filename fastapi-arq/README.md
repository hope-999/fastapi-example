# FastAPI + ARQ 完整示例

对应文章：《Celery 太重了？试试 ARQ：FastAPI 异步任务的新选择》

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动 Redis

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### 3. 启动 Worker

```bash
arq worker.WorkerSettings
```

> 加 `--burst` 可以让 Worker 处理完所有任务后自动退出，适合 cron 场景：
> ```bash
> arq worker.WorkerSettings --burst
> ```

### 4. 启动 FastAPI 服务

```bash
uvicorn main:app --reload
```

### 5. 测试 API

```bash
# 投递邮件任务
curl -X POST http://localhost:8000/send-email \
  -H "Content-Type: application/json" \
  -d '{"to":"user@example.com","subject":"测试","body":"Hello ARQ"}'

# 投递报表任务
curl -X POST http://localhost:8000/report/123

# 查询任务状态
curl http://localhost:8000/job/<job_id>
```

## 项目结构

```
.
├── main.py              # FastAPI 应用 + 任务投递接口
├── worker.py            # ARQ Worker 配置 + 任务函数
├── demo.py              # Hello ARQ 独立示例
├── docker-compose.yml   # 一键启动：redis + web + worker
├── Dockerfile           # 容器构建
└── requirements.txt     # 依赖
```

## 生产部署

```bash
docker-compose up -d
```

横向扩展时，增加 worker 实例即可：

```bash
docker-compose up -d --scale worker=3
```

## 核心特性

- **原生异步**：enqueue 和 worker 都是 `async`，不阻塞事件循环
- **延迟执行**：支持 `_defer_by` 延迟投递
- **任务唯一性**：支持 `_job_id` 防重复投递
- **Cron 定时任务**：内置 cron 支持，无需额外 beat 进程
- **重试机制**：`Retry(defer=30)` 配合 `max_tries` 精细化控制
- **优雅关闭**：`job_completion_wait` 配合 Kubernetes 的 `terminationGracePeriodSeconds`
- **健康检查**：内置 `health_check_interval` 和 `health_check_key`

## 技术栈

- Python 3.11+
- FastAPI
- ARQ (Async Redis Queue)
- Redis 7
- Docker / Docker Compose
