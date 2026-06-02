"""上传接口"""

from fastapi import APIRouter, UploadFile, HTTPException
from typing import List
import asyncio
from .client import cos_client
from .config import get_cos_settings

router = APIRouter(prefix="/upload", tags=["上传"])
settings = get_cos_settings()

@router.post("/batch")
async def upload_batch(files: List[UploadFile]) -> dict:
    """批量上传接口"""
    if not files:
        raise HTTPException(400, "没有上传文件")
    if len(files) > settings.COS_UPLOAD_MAX_FILES:
        raise HTTPException(400, f"一次最多上传 {settings.COS_UPLOAD_MAX_FILES} 个文件")
    
    tasks = [
        cos_client.upload(f.file, f.filename, f.content_type or "application/octet-stream")
        for f in files
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success = []
    failed = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed.append({"file": files[i].filename, "error": str(result)})
        else:
            success.append(result)
    
    return {
        "total": len(files),
        "success": len(success),
        "failed": len(failed),
        "success_list": success,
        "failed_list": failed
    }
