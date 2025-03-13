from fastapi import FastAPI, HTTPException
from db import db
import uvicorn
from pydantic import BaseModel, EmailStr
from datetime import datetime

app = FastAPI()

# Модели данных
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    created_at: str

def hash_password(password: str) -> str:
    return password

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return True

# ------

@app.get("/")
def root():
    return {"message": "Server rabotaet"}

# (CREATE)
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):
    user_id = f"user_{user.username}"

    # Проверка, существует ли пользователь
    existing_user = db.get_document(user_id)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Хеширование пароля
    user_data = user.model_dump()
    user_data["password_hash"] = hash_password(user.password)
    user_data["created_at"] = datetime.now().isoformat()

    # Сохранение пользователя в Couchbase
    if not db.create_document(user_id, user_data):
        raise HTTPException(status_code=500, detail="Failed to create user")

    # Возвращаем данные пользователя
    return {
        "user_id": user_id,
        "username": user.username,
        "email": user.email,
        "created_at": user_data["created_at"]
    }

# (GET)
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    user = db.get_document(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user_id,
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"]
    }

# (DELETE)
@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    if not db.delete_document(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return None

# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)