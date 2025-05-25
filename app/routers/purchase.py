from fastapi import APIRouter, HTTPException, Depends, status
from app.auth_utils import get_current_user
from app.db import db_users
from app.models.schemas import UserProgressUpdate, PurchaseItem

router = APIRouter(prefix="/users", tags=["purchases"])

@router.post("/{user_id}/purchase", response_model=UserProgressUpdate)
def purchase_item(
    user_id: str,
    item: PurchaseItem,
    current_user: dict = Depends(get_current_user)
) -> UserProgressUpdate:
    if user_id != current_user.get("user_id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    user = db_users.get_document(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    progress = user.setdefault("progress", {})
    coins = progress.get("coins", 0)
    existing_items = progress.get("items", [])

    total_cost = (item.price or 0) * item.quantity

    if total_cost and coins < total_cost:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient coins")

    if total_cost:
        progress["coins"] = coins - total_cost
    else:
        # если цена не указана, оставляем прежний баланс
        progress["coins"] = coins

    item_map = {i["name"]: i.get("amount", 0) for i in existing_items}
    item_map[item.name] = item_map.get(item.name, 0) + item.quantity
    progress["items"] = [{"name": name, "amount": amt} for name, amt in item_map.items()]

    user["version"] = user.get("version", 0) + 1
    user["progress"] = progress
    if not db_users.create_document(user_id, user):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to save purchase")

    return UserProgressUpdate(
        passedLevel=progress.get("passedLevel"),
        points=progress.get("points"),
        coins=progress.get("coins"),
        items=progress.get("items")
    )
