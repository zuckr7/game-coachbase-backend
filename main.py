from fastapi import FastAPI, HTTPException, Depends, status
from db import db
import uvicorn
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, time
import uuid
from typing import Optional
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
import bcrypt
import requests

app = FastAPI()


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Модели данных
class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserProgressUpdate(BaseModel):
    passedLevel: Optional[int] = None
    items: Optional[list[dict]] = None  # Optional для patch 

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    created_at: str
    version: int

def generate_user_id() -> str:
    while True:
        user_id = str(uuid.uuid4())
        if not db._get_document(user_id):
            return user_id

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(user_id:str):
    payload = {
        "sub": user_id,
        "exp":datetime.now() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    }
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_bearer)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM],options={"require_exp": True})
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.get_document(user_id)
    if user is None:
        raise credentials_exception
    return user

# ------

@app.get("/")
def root():
    return {"message": "Server rabotaet"}

# (CREATE)
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):
    user_id = generate_user_id()

    existing_user = db.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    user_data = user.model_dump()
    user_data.pop("password", None)
    user_data["user_id"] = user_id
    user_data["password_hash"] = hash_password(user.password)
    user_data["created_at"] = datetime.now().isoformat()
    user_data["version"] = 1
    user_data["progress"] = {
        "passedLevel": 0,  # Начальный уровень
        "items": [
            {"name": "shield", "amount": 1},
            {"name": "booster", "amount": 1}
        ]  # Первый список предметов
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
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):

    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
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
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access forbidden")

    if not db.delete_document(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User with ID {user_id} deleted successfully"}

@app.patch("/users/{user_id}/progress")
async def update_progress(user_id:str, progress_update: UserProgressUpdate, current_user: dict = Depends(get_current_user)):
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    user = db.get_document(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["version"] += 1

    if progress_update.passedLevel is not None:
        user["progress"]["passedLevel"] = progress_update.passedLevel

    if progress_update.items is not None:
        # Получаем текущие предметы как словарь
        current_items = {
            item["name"]: item.get("amount", item.get("quantity", 0))  # Проверяем оба ключа
            for item in user["progress"].get("items", [])
        }
        
        # Проходим по предметам из запроса
        for new_item in progress_update.items:
            name = new_item.get("name")
            amount = new_item.get("amount", 0)
            if name in current_items:
                current_items[name] += amount
            else:
                current_items[name] = amount
        
        updated_items = [{"name": name, "amount": amt} for name, amt in current_items.items() if amt != 0]
        
        user["progress"]["items"] = updated_items

    if not db.create_document(user_id, user):
        raise HTTPException(status_code=500, detail="Failed to update progress")
    
    return {
        "message": "Progress updated",
        "user_id": user_id,
        "username": user["username"],
        "version": user["version"],
        "progress": user["progress"] 
    }
    
@app.get("/users/{user_id}/progress", response_model=UserProgressUpdate)
async def get_progress(user_id: str, current_user: dict = Depends(get_current_user)):
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    user = db.get_document(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user["progress"]

@app.post("/auth/login")
async def login (form_data: OAuth2PasswordRequestForm=Depends()):
    user = db.get_user_by_username(form_data.username)

    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    return {
        "access_token": create_access_token(user["user_id"]),
        "token_type": "bearer"
    }

# Эндпоинт для VK. клиент передает параметр vk_code
@app.post("/auth/vk")
async def vk_auth(vk_code: str):
    vk_client_id = os.getenv("VK_CLIENT_ID")
    vk_client_secret = os.getenv("VK_CLIENT_SECRET")
    vk_redirect_uri = os.getenv("VK_REDIRECT_URI")

    token_url = "https://oauth.vk.com/access_token"
    params = {
        "client_id": vk_client_id,
        "client_secret": vk_client_secret,
        "redirect_uri": vk_redirect_uri,
        "code": vk_code
    }
    token_response = requests.get(token_url, params=params)
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="VK authentication failed")
    token_data = token_response.json()

    vk_access_token = token_data.get("access_token")
    vk_user_id = token_data.get("user_id")
    if not vk_access_token or not vk_user_id:
        raise HTTPException(status_code=400, detail="Invalid VK response")
    
    # Получаем данные пользователя из VK
    user_info_url = "https://api.vk.com/method/users.get"
    params = {
        "user_ids": vk_user_id,
        "access_token": vk_access_token,
        "v": "5.131",
        "fields": "photo_100,domain"
    }

    user_response = requests.get(user_info_url, params=params)

    if user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="VK user info retrieval failed")
    
    user_info = user_response.json()
    if "response" not in user_info or not user_info["response"]:
        raise HTTPException(status_code=400, detail="VK user info not found")
    
    vk_user = user_info["response"][0]
    # Имя пользователя на основе VK ID
    username = f"vk_{vk_user.get('id')}"
    # VK не всегда возвращает email
    email = f"{username}@vk.com"
    existing_user = db.get_user_by_vk_id(str(vk_user.get("id")))

    if not existing_user:
        # Если пользователя нет, создаём его без пароля
        user_id = generate_user_id()
        new_user = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "created_at": datetime.now().isoformat(),
            "version": 1,
            "progress": {
                "passedLevel": 0,
                "items": [
                    {"name": "shield", "amount": 1},
                    {"name": "booster", "amount": 1}
                ]
            },
            "vk_id": vk_user.get("id")
        }
        if not db.create_document(user_id, new_user):
            raise HTTPException(status_code=500, detail="Failed to create user")
        user_record = new_user
    else:
        user_record = existing_user

    jwt_token = create_access_token(user_record["user_id"])
    return {
        "access_token": jwt_token,
        "token_type": "bearer"
    }



# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)