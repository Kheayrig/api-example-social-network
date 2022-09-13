from fastapi import APIRouter, Body, status, Depends
from starlette.responses import JSONResponse

from app.api.schema import APIResponse, Profile, ProfileSettings
from app.api.security import get_password_hash, get_user_by_token, verify_password
from app.db.repositories.feed_repository import FeedRepository
from app.db.repositories.media_repository import MediaRepository

from app.db.repositories.users_repository import UserRepository

router = APIRouter()


@router.get("/profile", response_model=Profile, tags=["profile"])
async def get_current_user(current_user: dict = Depends(get_user_by_token)):
    """
    get current user if authorized
    """
    del current_user['hash']
    return current_user


@router.put("/profile", tags=["profile"], response_model=APIResponse)
async def update_profile(user_info: ProfileSettings = Body(..., embed=True),
                         current_user: dict = Depends(get_user_by_token)):
    """
    update profile info/settings if authorized
    """
    verify_password(user_info.old_password, current_user['hash'])
    await UserRepository.update_names(current_user['id'], user_info.first_name, user_info.last_name)
    pwd = None
    if user_info.password is not None:
        pwd = get_password_hash(user_info.password)
    await UserRepository.update_data(current_user['id'], user_info.login, pwd)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content="Information successfully changed"
    )


@router.delete("/profile", tags=["profile"], response_model=APIResponse)
async def delete_profile(password: str = Body(..., embed=True),
                         current_user: dict = Depends(get_user_by_token)):
    """
    delete profile if authorized
    """
    verify_password(password, current_user['hash'])
    posts = await FeedRepository.get_user_posts(current_user['id'])
    for post in posts:
        await MediaRepository.del_post_media(post['id'])
        await FeedRepository.delete_post(post['id'])
    await UserRepository.delete_user_by_id(current_user['id'])
