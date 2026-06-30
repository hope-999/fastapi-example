# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app, get_session
from app.models import Hero, Team

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

def test_create_hero_and_team():
    # 创建 Team
    response = client.post("/teams?name=Avengers&headquarters=New York")
    assert response.status_code == 201
    team_id = response.json()["id"]
    
    # 创建 Hero
    response = client.post("/heroes", json={
        "name": "Iron Man",
        "secret_name": "Tony Stark",
        "age": 45,
        "team_id": team_id
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Iron Man"

def test_selectinload():
    # 先创建数据
    client.post("/teams?name=Guardians&headquarters=Space")
    client.post("/heroes", json={
        "name": "Star-Lord",
        "secret_name": "Peter Quill",
        "team_id": 1
    })
    
    # 测试 selectinload
    response = client.get("/heroes/selectinload")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_joinedload():
    response = client.get("/heroes/joinedload")
    assert response.status_code == 200
