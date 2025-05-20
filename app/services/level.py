import uuid
from app.db import db_levels

def generate_level_id() -> str:
    return str(uuid.uuid4())

def prepare_new_level(data: dict) -> dict:
    level_id = generate_level_id()
    new_level = {
        "level_id": level_id,
        "name": data["name"],
        "difficulty": data["difficulty"],
        "data": data["data"],
    }
    return new_level

def create_level_in_db(level_data: dict) -> bool:
    return db_levels.create_document(level_data["level_id"], level_data)

def get_level_by_id(level_id: str) -> dict:
    return db_levels.get_document(level_id)

def delete_level(level_id: str) -> bool:
    return db_levels.delete_document(level_id)

def get_all_levels() -> list:
    return db_levels.get_all_documents()
