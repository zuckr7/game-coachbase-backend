from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserProgressUpdate(BaseModel):
    passedLevel: Optional[int] = None
    items: Optional[list[dict]] = None

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    created_at: str
    version: int