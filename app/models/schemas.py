from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str

class UserProgressUpdate(BaseModel):
    passedLevel: Optional[int] = None
    points: Optional[int] = 0
    coins: Optional[int] = 0 
    items: Optional[list[dict]] = None

class UserResponse(BaseModel):
    user_id: str
    username: str
    created_at: datetime
    version: int

class LevelCreate(BaseModel):
    name: str
    difficulty: str
    data: dict[str, Any]

class Level(LevelCreate):
    level_id: str
    name: str
    difficulty: str
    data: dict[str, Any]