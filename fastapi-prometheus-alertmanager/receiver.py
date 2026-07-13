from fastapi import FastAPI, Request
import httpx
import json

app = FastAPI()

WECHAT_BOT_KEY = "your-bot-key-here"


@app.post("/webhook")
async def alert_receiver(request: Request):
    payload = await request.json()

    status = payload.get("status", "firing")
    alerts = payload.get("alerts", [])

    if not alerts:
        return {"ok": True}

    first_alert = alerts[0]
    summary = first_alert.get("annotations", {}).get("summary", "告警")
    description = first_alert.get("annotations", {}).get("description", "")
    severity = first_alert.get("labels", {}).get("severity", "unknown")
    generator_url = first_alert.get("generatorURL", "")

    emoji = "🔥" if status == "firing" else "✅"
    text = f"""{emoji} FastAPI 服务告警

【状态】{status.upper()}
【级别】{severity.upper()}
【摘要】{summary}
【详情】{description}
【数量】本次聚合 {len(alerts)} 条告警
【链接】{generator_url}
"""

    await send_wechat(text)
    return {"ok": True}


async def send_wechat(text: str):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={WECHAT_BOT_KEY}"
    async with httpx.AsyncClient() as client:
        await client.post(
            url,
            json={"msgtype": "text", "text": {"content": text}}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
