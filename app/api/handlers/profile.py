from fastapi import APIRouter, Body, HTTPException, status
from starlette.responses import JSONResponse

from app.api.schema import User, ProfileSettings, APIResponse
from app.api.security import get_password_hash, get_user_by_token

from app.db.base import DB
from app.db.repositories.users_repository import UserRepository

router = APIRouter()


@router.get("/profile", response_model=User, tags=["profile"])
async def get_current_user(access_token: str):
    """
    get current user if authorized
    """
    if UserRepository.con is None:
        await DB.connect_db()
    user = await get_user_by_token(access_token)
    del user['hash']
    return user


@router.put("/profile", tags=["profile"], response_model=APIResponse)
async def update_profile(user_info: ProfileSettings = Body(..., embed=True)):
    """
    update profile info/settings if authorized
    """
    if UserRepository.con is None:
        await DB.connect_db()
    user = await get_user_by_token(user_info.access_token)
    await UserRepository.update_names(user['id'], user_info.first_name, user_info.last_name)
    pwd = None
    if user_info.password is not None:
        pwd = get_password_hash(user_info.password)
    await UserRepository.update_data(user['id'], user_info.login, pwd)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Information successfully changed"
    )
