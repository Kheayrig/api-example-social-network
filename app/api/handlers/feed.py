from typing import List

from fastapi import APIRouter, UploadFile, status, Body, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.schema import PostCreate, APIResponse, Feed
from app.api.security import get_user_by_token, is_user_post

from app.db.repositories.like_repository import LikeRepository
from app.db.repositories.feed_repository import FeedRepository
from app.db.repositories.media_repository import MediaRepository

router = APIRouter()


@router.get("/feed/recommended", tags=["posts"], response_model=List[Feed])
async def get_recommended_feed(limit: int = 1):
    """
    get recommended feed, sorted by likes
    """
    feed = await FeedRepository.get_recommended_posts(limit)
    for post in feed:
        if post['media_count'] > 0:
            media = await MediaRepository.get_post_media(post['id'])
            if media is False:
                media = []
            post['media'] = media
        else:
            post['media'] = []
    return feed


@router.get("/feed/{post_id}", tags=["posts"], response_model=Feed)
async def get_post(post_id: int):
    """
    get post by id
    """
    feed = await FeedRepository.get_post(post_id)
    if feed['media_count'] > 0:
        media = await MediaRepository.get_post_media(post_id)
        feed['media'] = media
    else:
        feed['media'] = []
    return feed


@router.get("/feed", tags=["posts"], response_model=List[Feed])
async def get_feed(limit: int = 1, page: int = 0):
    """
    get all feed by limit with paging(optional), page starts from 0
    """
    feed = await FeedRepository.get_posts(limit, page)
    for post in feed:
        if post['media_count'] > 0:
            media = await MediaRepository.get_post_media(post['id'])
            post['media'] = media
        else:
            post['media'] = []
    return feed


@router.post("/feed", tags=["posts"], response_model=Feed, response_model_include={'id'}, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate = Body(..., embed=True),
                      current_user: dict = Depends(get_user_by_token)):
    """
    Add new post if authorized

    """
    post_id = await FeedRepository.create_post(current_user['id'], post.title, post.message)
    return post_id


@router.delete("/feed/{post_id}", tags=["posts"], response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, current_user: dict = Depends(get_user_by_token)):
    """
    delete post if authorized
    """
    await is_user_post(current_user['id'], post_id)
    await MediaRepository.del_post_media(post_id)
    await FeedRepository.delete_post(post_id)
    return None


@router.put("/feed/{post_id}/media", tags=["posts"], response_model=None)
async def upload_media_to_post(media: List[UploadFile], post_id: int,
                               current_user: dict = Depends(get_user_by_token)):
    """
    upload media to post if authorized
    """
    await is_user_post(current_user['id'], post_id)
    await MediaRepository.add_all_media(post_id, current_user['id'], media)
    return None


@router.put("/feed/{post_id}", tags=["posts"], response_model=None)
async def update_post_message_and_title(post_id: int, post: PostCreate = Body(..., embed=True),
                                        current_user: dict = Depends(get_user_by_token)):
    """
    update message and title in the post if authorized
    """
    await is_user_post(current_user['id'], post_id)
    await FeedRepository.update_post_message_title(post_id, post.message, post.title)
    return None


@router.post("/feed/{post_id}/like", tags=["posts"], response_model=APIResponse, status_code=status.HTTP_202_ACCEPTED)
async def like_post(post_id: int, current_user: dict = Depends(get_user_by_token)):
    """
    put a like to post if authorized
    """
    await FeedRepository.is_existed_post(post_id)
    await LikeRepository.like_post(current_user['id'], post_id)
    return {"message": "You liked post"}


@router.post("/feed/{post_id}/unlike", tags=["posts"], response_model=APIResponse, status_code=status.HTTP_202_ACCEPTED)
async def unlike_post(post_id: int, current_user: dict = Depends(get_user_by_token)):
    """
    remove like from post if authorized
    """
    await FeedRepository.is_existed_post(post_id)
    await LikeRepository.unlike_post(current_user['id'], post_id)
    return {"message": "You unliked post"}

