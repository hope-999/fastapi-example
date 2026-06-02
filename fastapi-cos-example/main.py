from fastapi import FastAPI
from cos_service.upload import router as upload_router
from cos_service.download import router as download_router

app = FastAPI(title="FastAPI COS 示例")

# 注册路由
app.include_router(upload_router)
app.include_router(download_router)

@app.get("/")
async def root():
    return {"message": "FastAPI COS 示例服务", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(main=app, host="0.0.0.0", port=8000)
