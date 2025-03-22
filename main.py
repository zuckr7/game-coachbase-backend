from fastapi import FastAPI, HTTPException
from db import db
import uvicorn
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

app = FastAPI()

# Модели данных
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserProgressUpdate(BaseModel):
    passedLevel: int
    items: list[dict]

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    created_at: str
    version: int

def generate_user_id() -> str:
    while True:
        user_id = str(uuid.uuid4())
        if not db.get_document(user_id):
            return user_id

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
    user_id = generate_user_id()

    # Проверка, существует ли пользователь
    # existing_user = db.get_document(f"user_{user.username}")
    # if existing_user:
    #     raise HTTPException(status_code=400, detail="Username already exists")
    # Do we need unique username (common sense tells me yes :c)

    user_data = user.model_dump()
    user_data["user_id"] = user_id
    user_data["password_hash"] = hash_password(user.password)
    user_data["created_at"] = datetime.now().isoformat()
    user_data["version"] = 1
    user_data["progress"] = {
        "passedLevel": 0,  # Начальный уровень
        "items": [
            {"name": "shield", "amount": 1},
            {"name": "booster", "amount": 1}
        ]  # Пустой список предметов
    }

    # Сохранение в Couchbase
    if not db.create_document(user_id, user_data):
        raise HTTPException(status_code=500, detail="Failed to create user")

    # Возвращаем данные пользователя
    return {
        "user_id": user_id,
        "username": user.username,
        "email": user.email,
        "created_at": user_data["created_at"],
        "version": user_data["version"]
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
        "created_at": user["created_at"],
        "version": user["version"]
    }

# (DELETE)
@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    if not db.delete_document(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User with ID {user_id} deleted successfully"}

#(UPDATE PROGRESS)
@app.put("/users/{user_id}/progress")
def update_progress(user_id:str, progress_update: UserProgressUpdate):
    user = db.get_document(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["version"] += 1
    user["progress"] = progress_update.model_dump()

    if not db.create_document(user_id, user):  # Из-за upsert при создании, перезапишет там же с новыми данными
        raise HTTPException(status_code=500, detail="Failed to update progress")

    return {
        "message": "Progress updated",
        "user_id": user_id,
        "username": user["username"],
        "version": user["version"] 
    }
    
@app.get("/users/{user_id}/progress", response_model=UserProgressUpdate)
def get_progress(user_id: str):
    user = db.get_document(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user["progress"]

# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)