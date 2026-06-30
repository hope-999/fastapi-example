# FastAPI + SQLModel N+1 查询问题与解决方案

[公众号文章] FastAPI 接口突然变慢？SQLModel 的 N+1 查询正在偷走你的性能

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/hope-999/fastapi-example.git
cd fastapi-example/fastapi-n1-article

# 2. 启动（Docker Compose）
docker-compose up -d

# 3. 测试接口
curl http://localhost:8000/health

# 4. 对比 N+1 vs selectinload
curl http://localhost:8000/heroes/naive         # N+1 问题
curl http://localhost:8000/heroes/selectinload  # 2 条 SQL
curl http://localhost:8000/heroes/joinedload    # 1 条 SQL
```

## 项目结构

```
fastapi-n1-article/
├── app/
│   ├── __init__.py
│   ├── config.py       # 数据库配置
│   ├── db.py           # 异步引擎 + Session 依赖注入
│   ├── main.py         # FastAPI 路由（含 N+1 演示 + 解法）
│   └── models.py       # Hero/Team SQLModel 模型 + Relationship
├── tests/
│   ├── test_main.py    # pytest 异步测试
│   └── locustfile.py   # 压测脚本
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 核心对比

| 加载方式 | SQL 条数 | 平均耗时 |
|---------|---------|---------|
| naive 懒加载 | 101 条 | 850ms |
| selectinload | 2 条 | 12ms |
| joinedload | 1 条 | 10ms |

## 关键 API

- `GET /heroes/naive` — N+1 问题演示（隐式查询）
- `GET /heroes/selectinload` — selectinload 预加载
- `GET /heroes/joinedload` — joinedload LEFT JOIN
- `GET /heroes/{id}/with-team` — 单条预加载
- `GET /teams/{id}/with-heroes` — 一对多预加载

## 压测

```bash
pip install locust
locust -f tests/locustfile.py
```
