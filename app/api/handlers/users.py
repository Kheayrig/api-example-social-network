from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from app.api.schema import User
from app.db.repositories.users_repository import UserRepository

router = APIRouter()


@router.get("/users/{user_id}", response_model=User, tags=["users"])
async def get_user_by_id(user_id: int = 1):
    """
    get user by id
    """
    user = await UserRepository.get_user_by_id(user_id)
    del user['login']
    del user['hash']
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({
                "payload": user,
                "message": "OK",
                "title": None,
                "code": status.HTTP_200_OK
            })
        )
