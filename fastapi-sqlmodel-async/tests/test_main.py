# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app, get_session
from app.models import Hero

# 内存数据库用于测试
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=True)

async def override_get_session():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_and_read_hero():
    # 创建
    response = client.post("/heroes", json={
        "name": "Deadpond",
        "secret_name": "Dive Wilson",
        "age": 25
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Deadpond"
    hero_id = data["id"]
    
    # 查询
    response = client.get(f"/heroes/{hero_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Deadpond"
