"""COS 异步客户端封装"""

import asyncio
import logging
from typing import AsyncGenerator
from qcloud_cos import CosConfig, CosS3Client, CosServiceError
from .config import get_cos_settings
from .exceptions import COSUploadError, COSDownloadError

logger = logging.getLogger(__name__)

class COSClient:
    """腾讯云 COS 异步客户端封装"""
    
    def __init__(self):
        self.settings = get_cos_settings()
        self.config = CosConfig(
            Region=self.settings.COS_REGION,
            SecretId=self.settings.COS_SECRET_ID,
            SecretKey=self.settings.COS_SECRET_KEY
        )
        self.client = CosS3Client(self.config)
        self._semaphore = asyncio.Semaphore(self.settings.COS_MAX_CONCURRENT)
    
    async def upload(
        self, 
        file_stream, 
        key: str, 
        content_type: str = "application/octet-stream"
    ) -> dict:
        """
        上传文件到 COS
        
        Args:
            file_stream: 文件流
            key: COS 存储路径
            content_type: MIME 类型
            
        Returns:
            dict: {key, etag, cost_ms}
            
        Raises:
            COSUploadError: 上传失败
        """
        async with self._semaphore:
            for attempt in range(self.settings.COS_MAX_RETRY):
                try:
                    start = asyncio.get_event_loop().time()
                    
                    def _upload():
                        return self.client.put_object(
                            Bucket=self.settings.COS_BUCKET,
                            Body=file_stream,
                            Key=key,
                            ContentType=content_type
                        )
                    
                    resp = await asyncio.to_thread(_upload)
                    cost = (asyncio.get_event_loop().time() - start) * 1000
                    
                    logger.info(f"上传成功: {key}, cost={cost:.0f}ms")
                    return {"key": key, "etag": resp["ETag"], "cost_ms": round(cost, 2)}
                    
                except CosServiceError as e:
                    logger.warning(f"上传失败(attempt={attempt+1}): {key}, {e}")
                    if attempt == self.settings.COS_MAX_RETRY - 1:
                        raise COSUploadError(f"上传失败: {key}, {e}")
                    await asyncio.sleep(0.5 * (attempt + 1))
                    
                except Exception as e:
                    logger.error(f"上传异常: {key}, {e}")
                    raise COSUploadError(f"上传异常: {key}")
    
    async def download_stream(self, key: str) -> AsyncGenerator[bytes, None]:
        """
        异步下载文件流
        
        Args:
            key: COS 文件 key
            
        Yields:
            bytes: 数据块
        """
        def _download():
            resp = self.client.get_object(
                Bucket=self.settings.COS_BUCKET, 
                Key=key
            )
            return resp["Body"].get_raw_stream()
        
        try:
            stream = await asyncio.to_thread(_download)
            while True:
                chunk = await asyncio.to_thread(stream.read, 64 * 1024)
                if not chunk:
                    break
                yield chunk
        except CosServiceError as e:
            logger.error(f"下载失败: {key}, {e}")
            raise COSDownloadError(f"下载失败: {key}")

# 全局单例
cos_client = COSClient()
