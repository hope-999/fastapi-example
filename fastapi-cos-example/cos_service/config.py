"""COS 配置管理"""

from pydantic_settings import BaseSettings
from functools import lru_cache

class COSSettings(BaseSettings):
    """COS 配置，从环境变量读取"""
    COS_SECRET_ID: str
    COS_SECRET_KEY: str
    COS_REGION: str = "ap-beijing"
    COS_BUCKET: str
    COS_MAX_CONCURRENT: int = 5
    COS_UPLOAD_MAX_FILES: int = 100
    COS_DOWNLOAD_MAX_FILES: int = 50
    COS_MAX_RETRY: int = 3
    
    class Config:
        env_file = ".env"
        env_prefix = ""  # 不加前缀，直接用 COS_xxx

@lru_cache
def get_cos_settings() -> COSSettings:
    return COSSettings()
