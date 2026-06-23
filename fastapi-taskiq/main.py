from fastapi import FastAPI
from fastapi import Depends
from broker import broker
from tasks import parse_pdf, health_check
from config import get_settings
from taskiq_fastapi import init_broker

app = FastAPI(title="FastAPI + Taskiq Demo")
init_broker(broker, app)


def get_current_user() -> dict:
    """模拟用户认证依赖"""
    return {"user_id": "demo-001", "name": "Demo User"}


@app.post("/upload")
async def upload(file_path: str, user: dict = Depends(get_current_user)):
    """提交 PDF 解析任务"""
    task = await parse_pdf.kiq(file_path=file_path)
    return {
        "task_id": task.task_id,
        "message": "任务已提交",
        "user": user["name"],
    }


@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""
    result = await broker.result_backend.get_result(task_id)
    if result is None:
        return {"task_id": task_id, "status": "PENDING"}
    return {
        "task_id": task_id,
        "status": "SUCCESS" if result.is_err is False else "FAILURE",
        "result": result.return_value,
    }


@app.get("/health")
async def health():
    """服务健康检查"""
    return {"status": "ok", "service": "fastapi-taskiq"}
