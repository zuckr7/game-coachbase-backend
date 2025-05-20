import uuid
from app.db import db_users
from app.auth_utils import hash_password
from datetime import datetime

def generate_user_id() -> str:
    while True:
        user_id = str(uuid.uuid4())
        if not db_users._get_document(user_id):
            return user_id

def create_user_in_db(user_data: dict) -> bool:
    return db_users.create_document(user_data["user_id"], user_data)

def get_user_by_username(username: str):
    return db_users.get_user_by_username(username)

def get_user_by_id(user_id: str):
    return db_users.get_document(user_id)

def delete_user(user_id: str) -> bool:
    return db_users.delete_document(user_id)

def prepare_new_user(data: dict) -> dict:
    user_id = generate_user_id()
    new_user = {
        "user_id": user_id,
        "username": data["username"],
        "created_at": datetime.now().isoformat(),
        "version": 1,
        "password_hash": hash_password(data["password"]),
        "progress": {
            "passedLevel": 0,
            "points": 0,
            "coins": 100,
            "items": [
                {"name": "shield", "amount": 1},
                {"name": "booster", "amount": 1}
            ]
        }
    }
    return new_user

def get_leaderboard_from_db():
    leaderboard_data = db_users.get_leaderboard(limit=10)
    if leaderboard_data:
        for user in leaderboard_data:
            user["created_at"] = datetime.fromisoformat(user["created_at"])
    return leaderboard_data

def get_all_users()->list:
    return db_users.get_all_documents()