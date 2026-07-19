from fastapi import FastAPI, Depends, HTTPException
from functools import partial

app = FastAPI()

# 假设已定义 get_current_user
from .02_nested import get_current_user, User

def check_permissions(required: list[str]):
    """带参数的依赖工厂：闭包捕获 required 权限列表"""
    def _check(user: User = Depends(get_current_user)):
        for perm in required:
            if perm not in user.permissions:
                raise HTTPException(403, f"缺少权限: {perm}")
        return user
    return _check

# 实际 User 模型需要 permissions 字段
class UserWithPerms(User):
    permissions: list[str] = ["order:read", "user:read"]

@app.get("/orders")
async def list_orders(
    user: UserWithPerms = Depends(check_permissions(["order:read"]))
):
    """同一个校验逻辑，不同路由传不同的权限列表"""
    return {"orders": [], "user": user.name}
