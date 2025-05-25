from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import Level, LevelCreate
from app.services import level as level_service
from app.auth_utils import check_ip
from typing import List

router = APIRouter(prefix="/levels",tags=["Levels"])

@router.get("/{level_id}", response_model=Level)
def get_level(level_id: str):
    level_data = level_service.get_level_by_id(level_id)
    if not level_data:
        raise HTTPException(status_code=404, detail="Level not found")
    return level_data

@router.post("/", response_model=Level, dependencies=[Depends(check_ip)])
def create_level(level: LevelCreate):
    level_dict = level_service.prepare_new_level(level.model_dump())
    created = level_service.create_level_in_db(level_dict)
    if not created:
        raise HTTPException(status_code=500, detail="Error saving level to database")
    return level_dict

@router.delete("/{level_id}", dependencies=[Depends(check_ip)])
def delete_level(level_id: str):
    deleted = level_service.delete_level(level_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Level not found or failed to delete")
    return {"detail": "Level deleted"}

@router.get("/", response_model=List[Level])
def get_all_levels_endpoint():
    levels = level_service.get_all_levels()
    if levels is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve levels")
    return levels