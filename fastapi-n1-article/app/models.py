# app/models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Team(SQLModel, table=True):
    __tablename__ = "team"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str
    
    heroes: List["Hero"] = Relationship(back_populates="team")

class Hero(SQLModel, table=True):
    __tablename__ = "hero"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = None
    
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    team: Optional[Team] = Relationship(back_populates="heroes")

class HeroCreate(SQLModel):
    name: str
    secret_name: str
    age: Optional[int] = None
    team_id: Optional[int] = None

class HeroRead(HeroCreate):
    id: int

class TeamRead(SQLModel):
    id: int
    name: str
    headquarters: str
