# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from .db import engine, init_db, get_session
from .models import Hero, Team, HeroCreate, HeroRead

app = FastAPI(title="FastAPI + SQLModel Async Demo")

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/heroes", response_model=list[HeroRead])
async def read_heroes(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Hero))
    heroes = result.scalars().all()
    return heroes

@app.get("/heroes/{hero_id}", response_model=HeroRead)
async def read_hero(hero_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Hero).where(Hero.id == hero_id)
    )
    hero = result.scalar_one_or_none()
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

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
