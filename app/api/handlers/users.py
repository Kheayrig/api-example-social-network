from fastapi import APIRouter, HTTPException, status

from app.api.schema import User
from app.db.base import DB
from app.db.repositories.users_repository import UserRepository

router = APIRouter()


@router.get("/users/{user_id}", response_model=User, tags=["users"])
async def get_user_by_id(user_id: int = 1):
    """
    get user by id
    """
    if UserRepository.con is None:
        await DB.connect_db()
    user = await UserRepository.get_user_by_id(user_id)
    del user['login']
    del user['hash']
    return {**user}
