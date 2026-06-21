#!/usr/bin/env python3
"""
FastAPI + ARQ 完整示例
对应文章：《Celery 太重了？试试 ARQ：FastAPI 异步任务的新选择》
"""

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel
from arq import create_pool
from arq.connections import RedisSettings
from arq.jobs import Job

# ------------------------------------------------------------------
# Redis 配置（支持环境变量，Docker 环境中 REDIS_HOST=redis）
# ------------------------------------------------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_SETTINGS = RedisSettings(host=REDIS_HOST, port=REDIS_PORT)


# ------------------------------------------------------------------
# ARQ 连接单例封装
# ------------------------------------------------------------------
class ArqConnection:
    """ARQ 连接单例，在 FastAPI lifespan 中管理生命周期。"""

    _redis = None

    @classmethod
    async def get(cls):
        if cls._redis is None:
            cls._redis = await create_pool(REDIS_SETTINGS)
        return cls._redis

    @classmethod
    async def close(cls):
        if cls._redis:
            await cls._redis.close()
            cls._redis = None


# ------------------------------------------------------------------
# FastAPI lifespan（替代 startup/shutdown 事件）
# ------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    await ArqConnection.get()
    yield
    await ArqConnection.close()


app = FastAPI(
    title="FastAPI + ARQ Demo",
    lifespan=lifespan,
)


# ------------------------------------------------------------------
# Pydantic 请求模型
# ------------------------------------------------------------------
class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str


class UniqueJobRequest(BaseModel):
    to: str
    subject: str
    body: str
    job_id: str | None = None


# ------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------
@app.post("/send-email")
async def send_email_endpoint(req: EmailRequest):
    """投递一封邮件任务，支持 5 秒延迟（反悔时间）。"""
    redis = await ArqConnection.get()
    job = await redis.enqueue_job(
        "send_email",
        req.to,
        req.subject,
        req.body,
        _defer_by=5,  # 延迟 5 秒执行，给用户反悔时间
    )
    return {"job_id": job.job_id, "status": "queued"}


@app.post("/report/{user_id}")
async def generate_report_endpoint(user_id: int):
    """投递报表生成任务。"""
    redis = await ArqConnection.get()
    job = await redis.enqueue_job("generate_report", user_id)
    return {"job_id": job.job_id, "status": "queued"}


@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """查询任务状态与结果。"""
    redis = await ArqConnection.get()
    job = Job(job_id=job_id, redis=redis)

    status = await job.status()
    info = await job.info()

    result = None
    if status == "complete":
        result = await job.result(timeout=1)

    return {
        "job_id": job_id,
        "status": status,
        "enqueue_time": info.enqueue_time.isoformat() if info and info.enqueue_time else None,
        "result": result,
    }


@app.post("/send-email/unique")
async def send_email_unique(req: UniqueJobRequest):
    """防重复投递：相同 job_id 的任务只会入队一次。"""
    redis = await ArqConnection.get()
    job_id = req.job_id or f"welcome_email_{req.to}"
    job = await redis.enqueue_job(
        "send_email",
        req.to,
        req.subject,
        req.body,
        _job_id=job_id,
    )
    if job is None:
        return {"error": "任务已在队列中", "job_id": job_id}
    return {"job_id": job.job_id, "status": "queued"}


@app.get("/")
async def root():
    return {"message": "FastAPI + ARQ Demo", "time": datetime.now().isoformat()}
