from fastapi import FastAPI, Depends, Header, HTTPException
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str

async def optional_auth(
    token: Optional[str] = Header(None)
) -> Optional[User]:
    """条件跳过依赖：token 为空时返回 None，不强制鉴权"""
    if token is None:
        return None
    # 实际项目中应调用 verify_token(token)
    return User(name="alice")

@app.get("/health")
async def health(user: Optional[User] = Depends(optional_auth)):
    """鉴权变成可选项：公开访问 / 带身份访问 都支持"""
    if user:
        return {"status": "ok", "user": user.name}
    return {"status": "ok"}
