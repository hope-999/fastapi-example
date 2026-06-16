# tasks.py
import asyncio
from celery_app import celery_app
from redis_client import redis_client

async def publish_progress(task_id: str, percent: int, status: str):
    """异步发布进度到 Redis"""
    await redis_client.publish(
        f"task_progress:{task_id}",
        {"task_id": task_id, "percent": percent, "status": status}
    )

@celery_app.task(bind=True)
def process_data_task(self, task_id: str, data: str):
    """
    模拟一个耗时任务，带实时进度推送
    
    bind=True 让 self 指向当前任务实例，可以更新状态
    """
    import time
    
    # 初始化 Redis 连接（Worker 进程里需要手动连）
    import asyncio
    asyncio.run(redis_client.connect())
    
    try:
        # 步骤 1：数据验证 (0% -> 20%)
        asyncio.run(publish_progress(task_id, 10, "正在验证数据..."))
        time.sleep(1)
        
        asyncio.run(publish_progress(task_id, 20, "数据验证完成"))
        time.sleep(0.5)
        
        # 步骤 2：处理数据 (20% -> 70%)
        total_steps = 5
        for i in range(total_steps):
            percent = 30 + int((i / total_steps) * 40)
            asyncio.run(publish_progress(
                task_id, percent, f"正在处理第 {i+1}/{total_steps} 批数据..."
            ))
            time.sleep(1.5)  # 模拟耗时操作
        
        # 步骤 3：生成报告 (70% -> 100%)
        asyncio.run(publish_progress(task_id, 80, "正在生成报告..."))
        time.sleep(1)
        
        asyncio.run(publish_progress(task_id, 100, "任务完成！"))
        
        return {"result": f"处理完成：{data}", "status": "success"}
        
    except Exception as e:
        asyncio.run(publish_progress(task_id, 0, f"任务失败：{str(e)}"))
        raise
    finally:
        asyncio.run(redis_client.disconnect())
