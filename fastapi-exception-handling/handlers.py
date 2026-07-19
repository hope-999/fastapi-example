import logging
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse

from exceptions import CustomHTTPException
from schemas import ErrorResponse


logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器：用户看到简洁信息，运维拿到完整堆栈"""

    if isinstance(exc, CustomHTTPException):
        # 业务异常：直接返回，不需要记录 error 级别日志
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                code=exc.code,
                message=exc.message,
                path=request.url.path,
            ).model_dump(),
        )

    # 未预期的系统异常：记录完整 traceback，用户只收到人话
    logger.error(
        "Unhandled exception at %s: %s\n%s",
        request.url.path,
        exc,
        traceback.format_exc(),
    )

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            code="INTERNAL_ERROR",
            message="服务器内部错误，请稍后重试",
            path=request.url.path,
        ).model_dump(),
    )
