# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from .db import engine, init_db, get_session
from .models import Hero, Team, HeroCreate, HeroRead, TeamRead

app = FastAPI(title="FastAPI + SQLModel N+1 Demo")

@app.on_event("startup")
async def on_startup():
    await init_db()

# N+1 问题演示（naive 写法）
@app.get("/heroes/naive")
async def read_heroes_naive(
    session: AsyncSession = Depends(get_session)
):
    """演示 N+1 问题：100 条 Hero 会触发 101 条 SQL"""
    result = await session.execute(select(Hero))
    heroes = result.scalars().all()
    
    # 遍历访问 team 触发隐式查询
    data = []
    for hero in heroes:
        team_name = hero.team.name if hero.team else None
        data.append({"hero": hero.name, "team": team_name})
    
    return data

# selectinload 解法
@app.get("/heroes/selectinload", response_model=list[HeroRead])
async def read_heroes_selectinload(
    session: AsyncSession = Depends(get_session)
):
    """selectinload 预加载：2 条 SQL 搞定"""
    result = await session.execute(
        select(Hero).options(selectinload(Hero.team))
    )
    heroes = result.scalars().all()
    return heroes

# joinedload 解法
@app.get("/heroes/joinedload", response_model=list[HeroRead])
async def read_heroes_joinedload(
    session: AsyncSession = Depends(get_session)
):
    """joinedload LEFT JOIN：1 条 SQL 搞定"""
    result = await session.execute(
        select(Hero).options(joinedload(Hero.team))
    )
    heroes = result.scalars().all()
    return heroes

# 单条 Hero 含 Team
@app.get("/heroes/{hero_id}/with-team")
async def read_hero_with_team(
    hero_id: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Hero)
        .where(Hero.id == hero_id)
        .options(selectinload(Hero.team))
    )
    hero = result.scalar_one_or_none()
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

# Team 含 Heroes（一对多预加载）
@app.get("/teams/{team_id}/with-heroes")
async def read_team_with_heroes(
    team_id: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Team)
        .where(Team.id == team_id)
        .options(selectinload(Team.heroes))
    )
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

# 创建 Hero
@app.post("/heroes", response_model=HeroRead, status_code=201)
async def create_hero(
    hero: HeroCreate,
    session: AsyncSession = Depends(get_session)
):
    db_hero = Hero(**hero.dict())
    session.add(db_hero)
    await session.commit()
    await session.refresh(db_hero)
    return db_hero

# 创建 Team
@app.post("/teams", status_code=201)
async def create_team(
    name: str,
    headquarters: str,
    session: AsyncSession = Depends(get_session)
):
    team = Team(name=name, headquarters=headquarters)
    session.add(team)
    await session.commit()
    await session.refresh(team)
    return team

@app.get("/health")
async def health_check():
    return {"status": "ok"}
