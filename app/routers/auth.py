from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from models.schemas import Token
from services.auth import authenticate_user, vk_authenticate
from security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password, verify_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    return {
        "access_token": create_access_token(user["user_id"]),
        "token_type": "bearer"
    }

@router.post("/vk", response_model=Token)
def vk_login(vk_code: str):
    auth_result = vk_authenticate(vk_code)
    return {
        "access_token": auth_result["access_token"],
        "token_type": "bearer"
    }
