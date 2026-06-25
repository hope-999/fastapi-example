"""
SSE 基础示例：FastAPI 实现 Server-Sent Events
演示最简单的 SSE 推送——定时发送消息
"""
import asyncio
import random
from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FastAPI SSE 基础示例")

# 允许跨域（前端调试需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def event_generator():
    """
    异步生成器：每秒钟发送一条带时间戳的消息
    SSE 格式要求：data: 内容\n\n
    """
    for i in range(10):
        data = {
            "index": i + 1,
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": f"实时消息 #{i + 1}",
            "random": random.randint(1000, 9999),
        }
        # SSE 格式：必须以 data: 开头，以 \n\n 结尾
        yield f"data: {data}\n\n"
        await asyncio.sleep(1)


@app.get("/stream")
async def stream():
    """
    SSE 接口：建立流式连接，持续推送数据

    ⚠️ 关键：media_type 必须是 text/event-stream
    """
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            # 禁用缓存，确保实时性
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/")
async def root():
    """首页：返回一个简单的 HTML 页面来测试 SSE"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SSE 基础示例</title>
        <style>
            body { font-family: 'JetBrains Mono', monospace; max-width: 600px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            #output { border: 1px solid #ddd; padding: 15px; min-height: 200px; background: #f9f9f9; border-radius: 8px; }
            .msg { padding: 8px; margin: 5px 0; background: white; border-radius: 4px; border-left: 3px solid #22d3ee; }
            .status { color: #999; font-size: 12px; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>🔥 FastAPI SSE 实时推送</h1>
        <div id="output"></div>
        <div class="status" id="status">连接中...</div>

        <script>
            const output = document.getElementById('output');
            const status = document.getElementById('status');
            const es = new EventSource('/stream');

            es.onopen = () => {
                status.textContent = '✅ 连接已建立';
                status.style.color = '#22d3ee';
            };

            es.onmessage = (e) => {
                const data = JSON.parse(e.data.replace(/'/g, '"'));
                const div = document.createElement('div');
                div.className = 'msg';
                div.innerHTML = `<strong>#${data.index}</strong> ${data.message} <span style="color:#999">${data.time}</span>`;
                output.appendChild(div);
                output.scrollTop = output.scrollHeight;
            };

            es.onerror = (e) => {
                status.textContent = '⚠️ 连接出错，浏览器会自动重连...';
                status.style.color = '#fb7185';
            };
        </script>
    </body>
    </html>
    """
    return html_content


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
