"""COS 自定义异常"""

class COSUploadError(Exception):
    """COS 上传异常"""
    pass

class COSDownloadError(Exception):
    """COS 下载异常"""
    pass
