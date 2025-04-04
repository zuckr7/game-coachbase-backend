import uuid
from db import db
from security import hash_password
from datetime import datetime

def generate_user_id() -> str:
    while True:
        user_id = str(uuid.uuid4())
        if not db._get_document(user_id):
            return user_id

def create_user_in_db(user_data: dict) -> bool:
    return db.create_document(user_data["user_id"], user_data)

def get_user_by_username(username: str):
    return db.get_user_by_username(username)

def get_user_by_id(user_id: str):
    return db.get_document(user_id)

def delete_user(user_id: str) -> bool:
    return db.delete_document(user_id)

def prepare_new_user(data: dict) -> dict:
    user_id = generate_user_id()
    new_user = {
        "user_id": user_id,
        "username": data["username"],
        "email": data["email"],
        "created_at": datetime.now().isoformat(),
        "version": 1,
        "password_hash": hash_password(data["password"]),
        "progress": {
            "passedLevel": 0,
            "items": [
                {"name": "shield", "amount": 1},
                {"name": "booster", "amount": 1}
            ]
        }
    }
    return new_user
