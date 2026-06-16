# connection_manager.py
from fastapi import WebSocket

class ConnectionManager:
    """管理所有活跃的 WebSocket 连接"""
    
    def __init__(self):
        # key: task_id, value: WebSocket 连接
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, task_id: str, websocket: WebSocket):
        """接受新连接并注册"""
        await websocket.accept()
        self.active_connections[task_id] = websocket
    
    def disconnect(self, task_id: str):
        """清理断开连接"""
        if task_id in self.active_connections:
            del self.active_connections[task_id]
    
    async def send_progress(self, task_id: str, data: dict):
        """向指定任务推送进度"""
        if task_id in self.active_connections:
            ws = self.active_connections[task_id]
            try:
                await ws.send_json(data)
            except Exception:
                # 发送失败，清理失效连接
                self.disconnect(task_id)

# 全局单例
manager = ConnectionManager()
