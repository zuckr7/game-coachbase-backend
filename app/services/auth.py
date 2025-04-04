import os
import requests
from datetime import datetime
from db import db
from services.user import generate_user_id, create_user_in_db
from security import create_access_token
from fastapi import HTTPException, status

def authenticate_user(username: str, password: str, verify_fn) -> dict:
    user = db.get_user_by_username(username)
    if not user or not verify_fn(password, user.get("password_hash", "")):
        return None
    return user

def vk_authenticate(vk_code: str):
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
    username = f"vk_{vk_user.get('id')}"
    email = f"{username}@vk.com"
    existing_user = db.get_user_by_vk_id(str(vk_user.get("id")))
    if not existing_user:
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
        if not create_user_in_db(new_user):
            raise HTTPException(status_code=500, detail="Failed to create user")
        user_record = new_user
    else:
        user_record = existing_user

    jwt_token = create_access_token(user_record["user_id"])
    return {"access_token": jwt_token, "user": user_record}
