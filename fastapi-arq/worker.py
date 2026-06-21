#!/usr/bin/env python3
"""
ARQ Worker 配置
启动命令：arq worker.WorkerSettings
或（Docker 中）：arq worker.WorkerSettings
"""

import asyncio
import os

from httpx import AsyncClient
from arq import create_pool
from arq.connections import RedisSettings
from arq.worker import func, Retry
from arq.cron import cron

# Redis 配置（支持环境变量）
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_SETTINGS = RedisSettings(host=REDIS_HOST, port=REDIS_PORT)


# ------------------------------------------------------------------
# 任务函数
# ------------------------------------------------------------------
async def send_email(ctx, to: str, subject: str, body: str):
    """异步发送邮件（模拟）"""
    await asyncio.sleep(1)  # 模拟网络请求
    print(f"[Worker] 邮件已发送至 {to}: {subject}")
    return f"邮件已发送至 {to}"


async def generate_report(ctx, user_id: int):
    """生成报表（模拟耗时操作）"""
    await asyncio.sleep(3)
    print(f"[Worker] 报表生成完成: user_id={user_id}")
    return {"user_id": user_id, "report_url": f"https://cdn.example.com/rpt_{user_id}.pdf"}


async def unstable_api_call(ctx, endpoint: str):
    """模拟不稳定的第三方 API 调用，支持重试。"""
    try:
        async with AsyncClient() as client:
            resp = await client.get(endpoint, timeout=5)
            resp.raise_for_status()
            return resp.json()
    except Exception:
        # 抛 Retry 异常，Worker 会自动重试
        raise Retry(defer=30)  # 30 秒后重试


async def download_content(ctx, url: str):
    """下载网页内容，返回文本长度（Hello ARQ 示例）"""
    session: AsyncClient = ctx["session"]
    response = await session.get(url)
    return len(response.text)


# ------------------------------------------------------------------
# Worker 生命周期钩子
# ------------------------------------------------------------------
async def startup(ctx):
    """Worker 启动时创建 HTTP 会话"""
    ctx["session"] = AsyncClient()
    print("[Worker] Startup: HTTP session created")


async def shutdown(ctx):
    """Worker 关闭时清理资源"""
    await ctx["session"].aclose()
    print("[Worker] Shutdown: HTTP session closed")


# ------------------------------------------------------------------
# WorkerSettings：ARQ 的核心配置类
# ------------------------------------------------------------------
class WorkerSettings:
    """ARQ Worker 配置。"""

    # 注册所有任务函数
    functions = [
        send_email,
        generate_report,
        func(unstable_api_call, max_tries=3, timeout=10),  # 最多重试 3 次，每次最多 10 秒
        func(generate_report, keep_result=3600),           # 结果保留 1 小时
        download_content,
    ]

    # 启动/关闭钩子
    on_startup = startup
    on_shutdown = shutdown

    # Redis 连接
    redis_settings = REDIS_SETTINGS

    # 定时任务（Cron）
    cron_jobs = [
        # 每天早上 9 点发送日报
        cron(send_email, name="daily_report", hour=9, minute=0)
    ]

    # 优雅关闭：收到 SIGTERM 后，等 30 秒让正在执行的任务完成
    job_completion_wait = 30

    # 健康检查
    health_check_interval = 30
    health_check_key = "arq:health"

    # 默认不保留结果，节省 Redis 内存（可被单个任务覆盖）
    keep_result = 0


# ------------------------------------------------------------------
# 独立任务投递脚本（直接运行：python worker.py）
# ------------------------------------------------------------------
async def main():
    """投递示例任务，方便本地测试。"""
    redis = await create_pool(REDIS_SETTINGS)
    for url in ("https://example.com", "https://github.com"):
        job = await redis.enqueue_job("download_content", url)
        print(f"任务已投递：{job.job_id}")
    await redis.close()


if __name__ == "__main__":
    asyncio.run(main())
