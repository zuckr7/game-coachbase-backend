from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional

from security import get_current_user
from db import db_users
from models.schemas import UserProgressUpdate

router = APIRouter(prefix="/users", tags=["purchases"])


class PurchaseItem(BaseModel):
    name: str = Field(..., title="Item Name")
    quantity: int = Field(..., gt=0, title="Quantity")
    price: Optional[float] = Field(None, title="Price (optional)")


@router.post("/{user_id}/purchase", response_model=UserProgressUpdate)
def purchase_item(
    user_id: str,
    item: PurchaseItem,
    current_user: dict = Depends(get_current_user)
) -> UserProgressUpdate:
    # 1) Проверяем права
    if user_id != current_user.get("user_id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    # 2) Загружаем пользователя
    user = db_users.get_document(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    progress = user.setdefault("progress", {})
    coins = progress.get("coins", 0)
    existing_items = progress.get("items", [])

    # 3) Считаем стоимость
    total_cost = (item.price or 0) * item.quantity

    # 4) Проверяем баланс
    if total_cost and coins < total_cost:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient coins")

    # 5) Списываем монеты
    if total_cost:
        progress["coins"] = coins - total_cost
    else:
        # если цена не указана, оставляем прежний баланс
        progress["coins"] = coins

    # 6) Обновляем инвентарь
    item_map = {i["name"]: i.get("amount", 0) for i in existing_items}
    item_map[item.name] = item_map.get(item.name, 0) + item.quantity
    progress["items"] = [{"name": name, "amount": amt} for name, amt in item_map.items()]

    # 7) Апдейт версии и сохраняем
    user["version"] = user.get("version", 0) + 1
    user["progress"] = progress
    if not db_users.create_document(user_id, user):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to save purchase")

    # 8) Возвращаем весь прогресс, включая coins
    return UserProgressUpdate(
        passedLevel=progress.get("passedLevel"),
        points=progress.get("points"),
        coins=progress.get("coins"),
        items=progress.get("items")
    )
