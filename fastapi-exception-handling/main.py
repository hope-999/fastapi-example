from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from exceptions import CustomHTTPException
from handlers import global_exception_handler
from logging_config import setup_logging

setup_logging()

app = FastAPI(title="FastAPI Exception Handling Demo")

# 注册全局异常处理器
app.add_exception_handler(Exception, global_exception_handler)


@app.get("/")
async def root():
    return {"message": "Hello, exception handling!"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """正常业务接口"""
    if item_id < 0:
        raise CustomHTTPException(
            status_code=400,
            code="INVALID_ITEM_ID",
            message="item_id 不能为负数",
        )
    return {"item_id": item_id}


@app.get("/divide")
async def divide(a: float, b: float):
    """会触发 ZeroDivisionError 的接口，测试系统异常处理"""
    result = a / b  # 当 b=0 时抛出 ZeroDivisionError
    return {"result": result}


@app.get("/health")
async def health():
    return {"status": "ok"}
