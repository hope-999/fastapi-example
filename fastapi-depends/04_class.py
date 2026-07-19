from fastapi import FastAPI, Depends

app = FastAPI()

class ConnectionPool:
    """类级别依赖：__call__ 让 FastAPI 把对象本身当成依赖工厂"""

    def __init__(self, max_size: int = 10):
        self.pool = []
        self.max_size = max_size

    def __call__(self):
        if not self.pool:
            self.pool.append(self._create_conn())
        return self.pool.pop()

    def _create_conn(self):
        return {"conn_id": id(self), "type": "db_connection"}

# 全局单例，状态在内存中保持
pool = ConnectionPool(max_size=5)

@app.get("/items")
async def get_items(conn = Depends(pool)):
    """FastAPI 自动调用 pool.__call__() 获取连接"""
    return {"conn": conn}
