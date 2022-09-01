import datetime

from fastapi import APIRouter, Body, HTTPException, status, Depends

from app.api.schema import User, Profile
from app.db.base import UserData, DB, FeedData
from app.api.security import get_password_hash, get_current_user

router = APIRouter()


@router.get("/profile", response_model=User)
async def get_profile(token: str):
    if UserData.con is None:
        await DB.connect_db()
    res = get_current_user(token)
    if res is not None:
        user = await UserData.get_user_by_login(res.login)
        if isinstance(user, dict):
            del user['hash']
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token has been expired or revoked"
            )


@router.put("/profile")
async def update_profile(token: str = Body(..., embed=True), user_info: Profile = Body(..., embed=True)):
    if UserData.con is None:
        await DB.connect_db()
    token = get_current_user(token)
    if token.login is not None:
        user = await UserData.get_user_by_login(token.login)
        if isinstance(user, dict):
            await UserData.update_names(user['id'], user_info.first_name, user_info.last_name)
            pwd = None
            if user_info.password is not None:
                pwd = get_password_hash(user_info.password)
            await UserData.update_data(user['id'], user_info.login, pwd)
            return {"message": "Information successfully changed"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has been expired or revoked"
        )
