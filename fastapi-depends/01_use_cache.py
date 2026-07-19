from fastapi import FastAPI, Depends
from datetime import datetime

app = FastAPI()

def get_timestamp():
    return datetime.now()

@app.get("/demo")
async def demo(
    t1: datetime = Depends(get_timestamp, use_cache=False),
    t2: datetime = Depends(get_timestamp, use_cache=False),
):
    """use_cache=False 保证每次调用都是新的实例"""
    return {"t1": t1, "t2": t2}
