---
title: FastAPI 依赖注入只会 get_db？这 5 个高阶用法，90% 的人没用过
summary: 你以为 Depends 只是用来传数据库连接的？它还能做缓存、嵌套、带参数工厂、条件跳过，以及类级别依赖。掌握这 5 个用法，路由守卫和权限校验直接上一个台阶。
author: 洛水之风
cover: /root/.openclaw/workspace/fastapi-log-persistence-v2/imgs/cover.jpeg
---

# FastAPI 依赖注入只会 get_db？这 5 个高阶用法，90% 的人没用过

大部分人写 FastAPI，第一次碰到 `Depends` 是为了把数据库连接注入路由。传一个 `get_db` 进去，用完自动关闭，确实很方便。但 `Depends` 的设计远不止数据库连接。这 5 个高阶用法，写生产级权限校验和链路复用时完全绕不开。💡

## 用法一：依赖缓存控制（use_cache）

同一个请求里，多个参数都依赖同一个 `get_db`，FastAPI 默认会缓存结果。如果你的依赖有副作用——比如生成时间戳、计数器——这个缓存反而是个坑。

```python
from fastapi import Depends

def get_timestamp():
    return datetime.now()

@app.get("/demo")
async def demo(
    t1: datetime = Depends(get_timestamp, use_cache=False),
    t2: datetime = Depends(get_timestamp, use_cache=False),
):
    return {"t1": t1, "t2": t2}
```

`use_cache=False` 保证每次调用都是新的实例。时间戳、随机数、UUID 生成器这类有副作用的依赖，记得关掉缓存。⚠️

## 用法二：嵌套依赖

依赖本身可以再依赖其他依赖。这种嵌套特性让复用变得极其干净：

```python
async def get_current_user(token: str = Header(...)):
    return verify_token(token)

async def require_admin(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(403, "需要管理员权限")
    return user

@app.get("/admin-only")
async def admin_only(user: User = Depends(require_admin)):
    return {"msg": "管理员可见"}
```

路由只需要声明 `Depends(require_admin)`，底层自动完成 token 解析 + 角色校验。权限层级越复杂，嵌套依赖的价值越大。🔥

## 用法三：带参数的依赖工厂

需要给依赖传参数时，别写全局变量，用 `functools.partial` 或者工厂闭包：

```python
from functools import partial

def check_permissions(required: list[str]):
    def _check(user: User = Depends(get_current_user)):
        for perm in required:
            if perm not in user.permissions:
                raise HTTPException(403, f"缺少权限: {perm}")
        return user
    return _check

@app.get("/orders")
async def list_orders(
    user: User = Depends(check_permissions(["order:read"]))
):
    return {"orders": []}
```

同一个校验逻辑，不同路由传不同的权限列表，一行声明搞定。💡

## 用法四：类级别依赖（依赖状态保持）

依赖不一定非得是函数。类级别依赖可以保存状态，实现连接池、计数器、限流器等有状态的组件：

```python
class ConnectionPool:
    def __init__(self, max_size: int = 10):
        self.pool = []
        self.max_size = max_size

    def __call__(self):
        if not self.pool:
            self.pool.append(create_conn())
        return self.pool.pop()

pool = ConnectionPool(max_size=5)

@app.get("/items")
async def get_items(conn = Depends(pool)):
    return {"conn_id": id(conn)}
```

类实例的 `__call__` 方法让 FastAPI 把对象本身当成依赖工厂。状态保持、参数预置、生命周期管理，都在一个类里解决。⚠️

## 用法五：条件跳过依赖

某些场景下，依赖不是必须的，比如内部健康检查接口不需要鉴权。FastAPI 没有内置 "skip"，但可以用 `Optional` + 默认值绕过：

```python
from typing import Optional

async def optional_auth(
    token: Optional[str] = Header(None)
) -> Optional[User]:
    if token is None:
        return None
    return verify_token(token)

@app.get("/health")
async def health(user: Optional[User] = Depends(optional_auth)):
    if user:
        return {"status": "ok", "user": user.name}
    return {"status": "ok"}
```

鉴权变成可选项，同一个接口既支持公开访问，也支持带身份信息的访问。💡

## 一个关键陷阱

依赖里抛出的异常，如果没有被上层捕获，会直接变成 500 返回给客户端。务必在依赖内部处理好校验失败，用 `HTTPException` 抛 4xx，而不是让原始异常裸奔。

依赖注入不是语法糖，是 FastAPI 架构的核心。用好它，你的路由函数可以保持纯粹——只关心业务逻辑，把认证、权限、连接、日志全部交给依赖层。🔥

---

## 系列回顾

- **异常处理** → 500 变优雅 JSON
- **日志持久化** → 日志不落盘，重启就丢
- **Redis 缓存** → 重复查询把数据库打崩
- **Prometheus 原生监控** → 服务崩了还没报警

🔥 完整源码都在 [github.com/hope-999/fastapi-example](https://github.com/hope-999/fastapi-example)，按目录找对应主题。

## 互动话题

你在生产环境里用 `Depends` 做过最复杂的事情是什么？多层嵌套？还是带状态的单例？评论区聊聊。✍️

回复 **「依赖注入」** 获取本文完整源码和配置。✍️🔥
