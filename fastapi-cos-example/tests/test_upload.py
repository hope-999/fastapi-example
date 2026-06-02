"""上传接口测试"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# 注意：这些测试需要有效的 COS 凭证
# 建议在 CI 中使用 mock 或在本地测试时设置 .env

class TestUpload:
    """上传测试"""
    
    def test_upload_empty(self):
        """测试空上传"""
        response = client.post("/upload/batch")
        assert response.status_code == 400
        assert "没有上传文件" in response.json()["detail"]
    
    def test_upload_too_many(self, monkeypatch):
        """测试超过文件数量限制"""
        # mock 最大文件数
        monkeypatch.setenv("COS_UPLOAD_MAX_FILES", "2")
        
        # 创建超过限制的假文件
        files = []
        for i in range(3):
            files.append(("files", (f"test{i}.txt", b"test content", "text/plain")))
        
        response = client.post("/upload/batch", files=files)
        assert response.status_code == 400
        assert "最多上传" in response.json()["detail"]

class TestDownload:
    """下载测试"""
    
    def test_download_empty(self):
        """测试空下载"""
        response = client.post("/download/batch", json={"keys": []})
        assert response.status_code == 400
        assert "没有指定下载文件" in response.json()["detail"]
    
    def test_download_too_many(self, monkeypatch):
        """测试超过文件数量限制"""
        monkeypatch.setenv("COS_DOWNLOAD_MAX_FILES", "2")
        
        response = client.post("/download/batch", json={"keys": ["1.txt", "2.txt", "3.txt"]})
        assert response.status_code == 400
        assert "最多下载" in response.json()["detail"]
