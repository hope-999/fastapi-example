import asyncio
import time
from typing import List

import httpx
from broker import broker
from config import get_settings


@broker.task
async def parse_pdf(file_path: str) -> dict:
    """模拟 PDF 解析任务"""
    await asyncio.sleep(1)  # 模拟耗时操作
    return {
        "file_path": file_path,
        "pages": 42,
        "keywords": ["FastAPI", "Taskiq", "async"],
        "processed_at": time.time(),
    }


@broker.task
async def send_email(to: str, subject: str, body: str) -> dict:
    """模拟发送邮件任务"""
    await asyncio.sleep(0.5)
    return {
        "to": to,
        "subject": subject,
        "status": "sent",
        "sent_at": time.time(),
    }


@broker.task(schedule=[{"cron": "*/5 * * * *"}])
async def health_check() -> dict:
    """每 5 分钟检查一次外部 API 可用性"""
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.github.com/status", timeout=5)
        if resp.status_code != 200:
            await send_alert.kiq(f"API 异常！状态码: {resp.status_code}")
    return {"status": resp.status_code, "ts": time.time()}


@broker.task
async def send_alert(message: str) -> dict:
    """发送告警通知"""
    print(f"[ALERT] {message}")
    return {"alert": message, "sent_at": time.time()}
