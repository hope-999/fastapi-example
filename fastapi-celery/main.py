import uuid
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from celery.result import AsyncResult
from tasks import process_image
from celery_app import celery_app

app = FastAPI()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """上传图片，异步投递压缩任务"""
    file_id = str(uuid.uuid4())[:8]
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 投递任务，立即返回 task_id
    task = process_image.delay(str(file_path), target_width=800)

    return {
        "task_id": task.id,
        "status": "submitted",
        "check_url": f"/tasks/{task.id}/status",
    }


@app.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """查询任务状态和进度"""
    task = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task.status,  # PENDING / PROGRESS / SUCCESS / FAILURE / RETRY
    }

    if task.status == "PROGRESS":
        response["progress"] = task.info.get("progress", 0)
        response["step"] = task.info.get("step", "")

    elif task.status == "SUCCESS":
        response["result"] = task.result

    elif task.status == "FAILURE":
        response["error"] = str(task.result)

    return response
