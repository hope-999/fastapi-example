# FastAPI 数据库连接池 — 生产环境配置示例

对应文章：[FastAPI 数据库连接池炸了？生产环境 502 的元凶找到了](https://mp.weixin.qq.com)

## 核心配置

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # 常备 20 个连接
    max_overflow=10,        # 突发流量缓冲
    pool_pre_ping=True,     # 连接健康检查
    pool_recycle=3600,      # 1 小时回收
    pool_timeout=30,        # 获取连接超时
    echo=False,
)
```

## 关键要点

| 参数 | 作用 | 推荐值 |
|------|------|--------|
| `pool_size` | 常备连接数 | `(CPU * 2) + 1` |
| `max_overflow` | 临时连接上限 | 10-20 |
| `pool_pre_ping` | 取连接前健康检查 | `True`（必开） |
| `pool_recycle` | 连接强制回收时间 | 3600 秒 |

## 运行

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

访问 `http://localhost:8000/health` 查看连接池状态。
