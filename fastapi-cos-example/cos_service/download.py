"""下载接口"""

import io
import zipfile
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from .client import cos_client
from .config import get_cos_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/download", tags=["下载"])
settings = get_cos_settings()

@router.post("/batch")
async def download_batch(keys: list[str]):
    """批量下载：打包为 ZIP 流式返回"""
    if not keys:
        raise HTTPException(400, "没有指定下载文件")
    if len(keys) > settings.COS_DOWNLOAD_MAX_FILES:
        raise HTTPException(400, f"一次最多下载 {settings.COS_DOWNLOAD_MAX_FILES} 个文件")
    
    async def zip_generator():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for key in keys:
                try:
                    file_buffer = io.BytesIO()
                    async for chunk in cos_client.download_stream(key):
                        file_buffer.write(chunk)
                    zf.writestr(key, file_buffer.getvalue())
                    
                    buffer.seek(0)
                    yield buffer.read()
                    buffer.seek(0)
                    buffer.truncate(0)
                except Exception as e:
                    logger.error(f"下载失败: {key}, {e}")
                    continue
        
        buffer.seek(0)
        yield buffer.read()
    
    return StreamingResponse(
        zip_generator(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=download_{len(keys)}_files.zip"
        }
    )
