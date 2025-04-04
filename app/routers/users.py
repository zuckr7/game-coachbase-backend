from fastapi import APIRouter, HTTPException, Depends
from models.schemas import UserCreate, UserResponse
from services.user import prepare_new_user, create_user_in_db, get_user_by_id, delete_user
from security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate):
    existing = get_user_by_id(user.username)  # или используйте отдельную функцию проверки
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = prepare_new_user(user.model_dump())
    if not create_user_in_db(new_user):
        raise HTTPException(status_code=500, detail="Failed to create user")
    return {
        "user_id": new_user["user_id"],
        "username": new_user["username"],
        "email": new_user["email"],
        "created_at": new_user["created_at"],
        "version": new_user["version"]
    }

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user_id,
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"],
        "version": user["version"]
    }

@router.delete("/{user_id}")
def remove_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    if not delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"User with ID {user_id} deleted successfully"}
