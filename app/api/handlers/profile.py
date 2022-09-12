from fastapi import APIRouter, Body, status, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import JSONResponse

from app.api.schema import User, ProfileSettings, APIResponse
from app.api.security import get_password_hash, get_user_by_token, verify_password
from app.db.repositories.feed_repository import FeedRepository
from app.db.repositories.media_repository import MediaRepository

from app.db.repositories.users_repository import UserRepository

router = APIRouter()


@router.get("/profile", response_model=User, tags=["profile"])
async def get_current_user(access_token: str = Depends(OAuth2PasswordBearer(tokenUrl="/auth/token"))):
    """
    get current user if authorized
    """
    user = await get_user_by_token(access_token)
    del user['hash']
    return user


@router.put("/profile", tags=["profile"], response_model=APIResponse)
async def update_profile(user_info: ProfileSettings = Body(..., embed=True), access_token: str = Depends(OAuth2PasswordBearer(tokenUrl="/auth/token"))):
    """
    update profile info/settings if authorized
    """
    user = await get_user_by_token(access_token)
    verify_password(user_info.old_password, user['hash'])
    await UserRepository.update_names(user['id'], user_info.first_name, user_info.last_name)
    pwd = None
    if user_info.password is not None:
        pwd = get_password_hash(user_info.password)
    await UserRepository.update_data(user['id'], user_info.login, pwd)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Information successfully changed"
    )


@router.delete("/profile", tags=["profile"], response_model=APIResponse)
async def delete_profile(password: str = Body(..., embed=True),
                         access_token: str = Depends(OAuth2PasswordBearer(tokenUrl="/auth/token"))):
    """
    delete profile if authorized
    """
    user = await get_user_by_token(access_token)
    verify_password(password, user['hash'])
    posts = await FeedRepository.get_user_posts(user['id'])
    for post in posts:
        await MediaRepository.del_post_media(post['id'])
        await FeedRepository.delete_post(post['id'])
    await UserRepository.delete_user_by_id(user['id'])
