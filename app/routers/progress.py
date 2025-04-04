from fastapi import APIRouter, HTTPException, Depends
from models.schemas import UserProgressUpdate
from db import db
from security import get_current_user

router = APIRouter(prefix="/users", tags=["progress"])

@router.patch("/{user_id}/progress")
def update_progress(user_id: str, progress_update: UserProgressUpdate, current_user: dict = Depends(get_current_user)):
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    user = db.get_document(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["version"] += 1

    if progress_update.passedLevel is not None:
        user["progress"]["passedLevel"] = progress_update.passedLevel

    if progress_update.items is not None:
        current_items = {
            item["name"]: item.get("amount", item.get("quantity", 0))
            for item in user["progress"].get("items", [])
        }
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

@router.get("/{user_id}/progress", response_model=UserProgressUpdate)
def get_progress(user_id: str, current_user: dict = Depends(get_current_user)):
    if user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    user = db.get_document(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user["progress"]
