from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    """统一错误响应模型"""

    code: str
    message: str
    path: str
    detail: Optional[str] = None
