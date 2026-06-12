# 别让 FastAPI 的异步骗了你：Celery 才是后台任务的正确解法

完整示例代码，配套公众号文章。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动 Redis
docker run -d -p 6379:6379 --name redis redis:alpine

# 3. 启动 Celery Worker
celery -A celery_app worker --loglevel=info -P threads

# 4. 启动 FastAPI
uvicorn main:app --reload

# 5. 测试上传
curl -X POST -F "file=@your_photo.jpg" http://localhost:8000/upload
```

## Docker Compose 一键部署

```bash
docker-compose up --build
```

访问 `http://localhost:5555` 打开 Flower 监控面板。

## 项目结构

```
fastapi-celery/
├── config.py        # 配置集中管理
├── celery_app.py    # Celery 实例化
├── tasks.py         # 任务定义
├── main.py          # FastAPI 应用
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```
