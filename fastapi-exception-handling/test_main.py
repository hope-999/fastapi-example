from fastapi.testclient import TestClient
import pytest

from main import app


client = TestClient(app)


class TestCustomHTTPException:
    """测试自定义业务异常"""

    def test_valid_item(self):
        response = client.get("/items/1")
        assert response.status_code == 200
        assert response.json() == {"item_id": 1}

    def test_negative_item_id(self):
        response = client.get("/items/-1")
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "INVALID_ITEM_ID"
        assert "不能为负数" in data["message"]
        assert data["path"] == "/items/-1"


class TestSystemException:
    """测试未捕获的系统异常"""

    def test_zero_division(self):
        response = client.get("/divide?a=1&b=0")
        assert response.status_code == 500
        data = response.json()
        assert data["code"] == "INTERNAL_ERROR"
        assert "服务器内部错误" in data["message"]
        assert data["path"] == "/divide"
        # 确保不暴露原始异常信息
        assert "ZeroDivisionError" not in str(data)
        assert "traceback" not in str(data)


class TestHealth:
    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
