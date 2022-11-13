from fastapi import APIRouter, Body, status, Depends

from app.api.schema import ProfileSettings, User
from app.api.security import get_password_hash, get_user_by_token, verify_password
from app.db.repositories.feed_repository import FeedRepository
from app.db.repositories.like_repository import LikeRepository
from app.db.repositories.media_repository import MediaRepository

from app.db.repositories.users_repository import UserRepository

router = APIRouter()


@router.get("/profile", response_model=User, tags=["profile"])
async def get_current_user(current_user: dict = Depends(get_user_by_token)):
    """
    get current user if authorized
    """
    return current_user


@router.put("/profile", tags=["profile"], response_model=None)
async def update_profile(user_info: ProfileSettings = Body(..., embed=True),
                         current_user: dict = Depends(get_user_by_token)):
    """
    update profile info/settings if authorized
    """
    verify_password(user_info.old_password, current_user['hash'])
    data = user_info.dict(exclude_none=True)
    if 'password' in data:
        data['hash'] = get_password_hash(user_info.password)
        del data['password']
    del data['old_password']
    await UserRepository.update_data(current_user['id'], data)
    return None


@router.delete("/profile", tags=["profile"], response_model=None, status_code=status.HTTP_204_NO_CONTENT)
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
    await LikeRepository.delete_all_user_likes(current_user['id'])
    await UserRepository.delete_user(current_user['id'])
    return None
