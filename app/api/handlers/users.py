import datetime

from fastapi import APIRouter, Body, HTTPException, status

from app.api.schema import User
from app.db.base import UserData, DB

router = APIRouter()


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int = 1):
    if UserData.con is None:
        await DB.connect_db()
    user = await UserData.get_user_by_id(user_id)
    del user['login']
    del user['hash']
    if user is not False:
        return {**user}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid id"
        )
