"""
AI 打字机效果：FastAPI + SSE 流式调用 LLM
演示如何实现 ChatGPT 式的逐字输出效果
"""
import asyncio
import os

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 加载环境变量（OPENAI_API_KEY）
load_dotenv()

app = FastAPI(title="FastAPI SSE AI 打字机")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 可选：如果安装了 openai 库，就用它；否则用模拟数据
# pip install openai
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_REAL_LLM = bool(OPENAI_API_KEY)

if USE_REAL_LLM:
    try:
        import openai
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    except ImportError:
        USE_REAL_LLM = False


async def mock_llm_stream(message: str):
    """
    模拟 LLM 流式输出（用于演示，无需 API Key）
    将回复拆分成多个 token 逐字 yield
    """
    mock_response = (
        f"这是一个模拟的流式响应。"
        f"你发送的消息是：「{message}」。"
        f"在实际运行中，这里会连接到 OpenAI 或 Claude 的 API，"
        f"每个 token 都会实时推送到前端，实现打字机效果。"
        f"SSE 让这一切变得极其简单——几行代码，无需 WebSocket。"
    )

    # 模拟逐字输出
    words = mock_response.split()
    for word in words:
        yield word + " "
        await asyncio.sleep(0.1)  # 模拟网络延迟

    yield "[DONE]"


async def real_llm_stream(message: str):
    """
    真实的 OpenAI 流式调用
    ⚠️ 需要配置 OPENAI_API_KEY 环境变量
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message}],
            stream=True,  # 🔥 关键：开启流式模式
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                yield token

        yield "[DONE]"

    except Exception as e:
        yield f"[ERROR] LLM 调用失败: {str(e)}"


async def chat_stream(message: str):
    """
    SSE 生成器：将 LLM 输出包装为 SSE 格式
    """
    stream_func = real_llm_stream if USE_REAL_LLM else mock_llm_stream

    async for token in stream_func(message):
        if token == "[DONE]":
            yield "data: [DONE]\n\n"
            break
        elif token.startswith("[ERROR]"):
            yield f"data: {token}\n\n"
            break
        else:
            yield f"data: {token}\n\n"


@app.get("/chat")
async def chat(message: str):
    """
    SSE 接口：流式返回 LLM 输出

    前端调用：new EventSource('/chat?message=你好')
    """
    return StreamingResponse(
        chat_stream(message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/")
async def index():
    """
    提供一个简单的 HTML 页面来测试 AI 打字机效果
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AI 打字机效果</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 700px; margin: 40px auto; padding: 20px;
                background: #f5f5f5;
            }
            .chat-container {
                background: white; border-radius: 12px; padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); min-height: 400px;
            }
            .input-area {
                display: flex; gap: 10px; margin-top: 20px;
            }
            input {
                flex: 1; padding: 12px 16px; border: 1px solid #ddd;
                border-radius: 8px; font-size: 16px;
            }
            button {
                padding: 12px 24px; background: #22d3ee; color: white;
                border: none; border-radius: 8px; cursor: pointer; font-size: 16px;
            }
            button:hover { background: #06b6d4; }
            #output {
                min-height: 200px; padding: 15px;
                background: #f9fafb; border-radius: 8px;
                line-height: 1.6; white-space: pre-wrap;
            }
            .cursor {
                display: inline-block; width: 2px; height: 1.2em;
                background: #22d3ee; animation: blink 1s infinite;
                vertical-align: text-bottom; margin-left: 2px;
            }
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0; }
            }
            .status {
                color: #999; font-size: 12px; margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <h2>🤖 AI 打字机效果</h2>
            <div id="output"></div>
            <span class="cursor" id="cursor" style="display:none"></span>
            <div class="status" id="status">输入问题，点击发送</div>
        </div>
        <div class="input-area">
            <input type="text" id="message" placeholder="输入你的问题..." value="什么是 SSE？"
                   onkeypress="if(event.key==='Enter')send()">
            <button onclick="send()">发送</button>
        </div>

        <script>
            const output = document.getElementById('output');
            const cursor = document.getElementById('cursor');
            const status = document.getElementById('status');
            const messageInput = document.getElementById('message');

            function send() {
                const message = messageInput.value.trim();
                if (!message) return;

                output.textContent = '';
                cursor.style.display = 'inline-block';
                status.textContent = '连接中...';
                status.style.color = '#22d3ee';

                const es = new EventSource('/chat?message=' + encodeURIComponent(message));

                es.onopen = () => {
                    status.textContent = '✅ 已连接，正在接收流式输出...';
                };

                es.onmessage = (e) => {
                    if (e.data === '[DONE]') {
                        es.close();
                        cursor.style.display = 'none';
                        status.textContent = '✅ 输出完成';
                        status.style.color = '#34d399';
                        return;
                    }
                    if (e.data.startsWith('[ERROR]')) {
                        es.close();
                        cursor.style.display = 'none';
                        status.textContent = e.data;
                        status.style.color = '#fb7185';
                        return;
                    }
                    output.textContent += e.data;
                };

                es.onerror = (e) => {
                    status.textContent = '⚠️ 连接出错';
                    status.style.color = '#fb7185';
                    cursor.style.display = 'none';
                };
            }

            // 页面加载后自动发送一次示例
            window.onload = () => messageInput.focus();
        </script>
    </body>
    </html>
    """
    return html_content


if __name__ == "__main__":
    import uvicorn
    print(f"🚀 启动 SSE 服务 | 使用真实 LLM: {USE_REAL_LLM}")
    if not USE_REAL_LLM:
        print("💡 提示：设置 OPENAI_API_KEY 环境变量可连接真实 LLM")
    uvicorn.run(app, host="0.0.0.0", port=8000)
