#!/usr/bin/env python3
"""
Hello ARQ 独立示例（对应文章第二节）
直接运行：python demo.py
"""

import asyncio
from httpx import AsyncClient
from arq import create_pool
from arq.connections import RedisSettings

REDIS_SETTINGS = RedisSettings()


async def download_content(ctx, url: str):
    """下载网页内容，返回文本长度"""
    session: AsyncClient = ctx["session"]
    response = await session.get(url)
    return len(response.text)


async def startup(ctx):
    """Worker 启动时创建 HTTP 会话"""
    ctx["session"] = AsyncClient()


async def shutdown(ctx):
    """Worker 关闭时清理资源"""
    await ctx["session"].aclose()


class WorkerSettings:
    functions = [download_content]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = REDIS_SETTINGS


async def main():
    redis = await create_pool(REDIS_SETTINGS)
    for url in ("https://example.com", "https://github.com"):
        job = await redis.enqueue_job("download_content", url)
        print(f"任务已投递：{job.job_id}")
    await redis.close()


if __name__ == "__main__":
    asyncio.run(main())
