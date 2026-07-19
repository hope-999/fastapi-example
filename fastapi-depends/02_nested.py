from fastapi import FastAPI, Depends, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    is_admin: bool

async def get_current_user(token: str = Header(...)):
    """从 Header 提取 token 并解析用户"""
    # 实际项目中应调用 verify_token(token)
    return User(name="alice", is_admin=True)

async def require_admin(user: User = Depends(get_current_user)):
    """嵌套依赖：依赖 get_current_user，增加管理员校验"""
    if not user.is_admin:
        raise HTTPException(403, "需要管理员权限")
    return user

@app.get("/admin-only")
async def admin_only(user: User = Depends(require_admin)):
    """路由只声明 Depends(require_admin)，底层自动完成 token 解析 + 角色校验"""
    return {"msg": "管理员可见", "user": user.name}
