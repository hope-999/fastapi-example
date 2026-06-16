# main.py
import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from celery_app import celery_app
from connection_manager import manager
from redis_client import redis_client
from tasks import process_data_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时连接 Redis
    await redis_client.connect()
    print("✅ Redis 连接成功")
    yield
    # 关闭时清理
    await redis_client.disconnect()
    print("🛑 Redis 连接已关闭")


app = FastAPI(title="FastAPI WebSocket + Celery 演示", lifespan=lifespan)

# 挂载静态文件（前端页面）
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/api/tasks")
async def create_task(data: str = "default_data"):
    """
    创建异步任务
    
    返回 task_id，前端用这个 ID 连接 WebSocket
    """
    task = process_data_task.delay(data)
    return {
        "task_id": task.id,
        "status": "submitted",
        "message": "任务已提交，请通过 WebSocket 监听进度"
    }


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket 端点：实时推送任务进度
    
    1. 接受前端连接
    2. 订阅 Redis 频道
    3. 收到消息后推给前端
    4. 任务完成或断开时清理
    """
    await manager.connect(task_id, websocket)
    
    try:
        # 订阅 Redis 频道
        async with redis_client.subscribe(f"task_progress:{task_id}") as pubsub:
            while True:
                # 非阻塞获取消息
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                
                if message:
                    # 解析并推送
                    data = json.loads(message["data"])
                    await manager.send_progress(task_id, data)
                    
                    # 任务完成，关闭连接
                    if data.get("percent") == 100:
                        await websocket.close()
                        break
                
                # 检查前端是否还连着
                try:
                    await asyncio.wait_for(
                        websocket.receive_text(), timeout=0.1
                    )
                except asyncio.TimeoutError:
                    pass  # 正常超时，继续循环
                    
    except WebSocketDisconnect:
        print(f"📴 客户端断开：{task_id}")
    except Exception as e:
        print(f"❌ WebSocket 错误：{e}")
    finally:
        manager.disconnect(task_id)


@app.get("/")
async def root():
    """首页，返回前端演示页面链接"""
    return {
        "message": "FastAPI + WebSocket + Celery 实时进度演示",
        "demo": "/static/index.html",
        "docs": "/docs"
    }
