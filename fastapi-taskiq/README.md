# FastAPI + Taskiq 异步任务队列示例

> 配套文章：「Celery 不够轻？Taskiq 5 行代码搞定」

## 项目结构

```
fastapi-taskiq/
├── main.py              # FastAPI 应用
├── broker.py            # Taskiq Broker 定义
├── tasks.py             # 后台任务
├── config.py            # 配置管理
├── scheduler.py         # 定时任务调度器
├── requirements.txt     # Python 依赖
├── Dockerfile           # Docker 镜像
├── docker-compose.yml   # Docker Compose 部署
└── README.md            # 本文档
```

## 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动 Redis
docker run -d -p 6379:6379 redis:7-alpine

# 3. 启动 FastAPI 服务
uvicorn main:app --reload

# 4. 启动 Worker（新终端）
taskiq worker broker:broker --fs-discover --reload

# 5. 启动定时任务调度器（新终端）
taskiq scheduler scheduler:scheduler
```

## 测试接口

```bash
# 提交 PDF 解析任务
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/tmp/upload.pdf"}'
```

## Docker Compose 一键部署

```bash
docker-compose up -d
```

- Web: http://localhost:8000
- Redis: localhost:6379

## 技术要点

1. **异步原生** — Taskiq 原生支持 asyncio，无需 sync → async 桥接
2. **依赖复用** — FastAPI 的 `Depends` 在 Worker 中直接生效
3. **强类型** — PEP 612 类型提示，IDE 自动补全
4. **定时任务** — 内置调度器，无需单独的 Beat 进程

## 踩坑提示

- 任务参数必须可序列化（Pydantic），不要传文件对象或数据库连接句柄
- Worker 数量：CPU 密集型 ≈ CPU 核数，IO 密集型可适当增加
- Redis 结果设置过期时间，避免撑爆内存
