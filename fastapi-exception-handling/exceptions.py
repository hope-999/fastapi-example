from fastapi import HTTPException


class CustomHTTPException(HTTPException):
    """自定义业务异常，携带 code + message 给前端"""

    def __init__(self, status_code: int, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(
            status_code=status_code,
            detail=message,
        )
