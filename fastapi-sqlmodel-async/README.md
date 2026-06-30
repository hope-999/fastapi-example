# FastAPI + SQLModel 异步查询示例

[公众号文章] FastAPI 数据库查询又卡住了？SQLModel 异步模式 5 分钟救场

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/hope-999/fastapi-example.git
cd fastapi-sqlmodel-async

# 2. 启动（Docker Compose）
docker-compose up -d

# 3. 测试接口
curl http://localhost:8000/health
curl http://localhost:8000/heroes
```

## 项目结构

```
fastapi-sqlmodel-async/
├── app/
│   ├── __init__.py
│   ├── config.py       # 数据库配置
│   ├── db.py           # 异步引擎 + Session 依赖注入
│   ├── main.py         # FastAPI 路由
│   └── models.py       # SQLModel 数据模型
├── tests/
│   └── test_main.py    # 异步测试示例
├── imgs/               # 文章配图
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 4 个必避的坑

| 坑 | 解法 |
|---|---|
| `metadata.create_all` 异步报错 | 包 `conn.run_sync()` |
| 提交后访问属性报 MissingGreenlet | 加 `expire_on_commit=False` |
| `session.exec()` 在异步下不可用 | 改用 `session.execute()` |
| 关系属性隐式查询炸 | 用 `selectinload` 预加载 |

## 压测

```bash
pip install locust
locust -f tests/locustfile.py
```
