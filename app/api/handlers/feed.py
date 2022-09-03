from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, status, Body
from fastapi.responses import JSONResponse

from app.api.schema import PostCreate, APIResponse, Feed
from app.api.security import get_user_by_token, is_existed_post, is_user_post

from app.db.base import DB
from app.db.repositories.like_repository import LikeRepository
from app.db.repositories.feed_repository import FeedRepository
from app.db.repositories.media_repository import MediaRepository

router = APIRouter()


@router.get("/feed/recommended", tags=["posts"], response_model=List[Feed])
async def get_recommended_feed(limit: int = 1):
    """
    get recommended feed, sorted by likes
    """
    if FeedRepository.con is None:
        await DB.connect_db()
    feed = await FeedRepository.get_recommended_posts(limit)
    if isinstance(feed, list):
        for post in feed:
            if post['media_count'] > 0:
                media = await MediaRepository.get_post_media(post['id'])
                if media is False:
                    media = []
                post['media'] = media
            else:
                post['media'] = []
        return feed
    else:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No post found"
        )


@router.get("/feed/{post_id}", tags=["posts"], response_model=Feed)
async def get_post(post_id: int):
    """
    get post by id
    """
    if FeedRepository.con is None:
        await DB.connect_db()
    feed = await is_existed_post(post_id)
    if feed['media_count'] > 0:
        media = await MediaRepository.get_post_media(post_id)
        if media is False:
            media = []
        feed['media'] = media
    else:
        feed['media'] = []
    return feed


@router.get("/feed", tags=["posts"], response_model=List[Feed])
async def get_feed(limit: int = 1, page: int = 0):
    """
    get all feed by limit with paging(optional)
    """
    if FeedRepository.con is None:
        await DB.connect_db()
    feed = await FeedRepository.get_posts(limit, page)
    if isinstance(feed, list):
        for post in feed:
            if post['media_count'] > 0:
                media = await MediaRepository.get_post_media(post['id'])
                if media is False:
                    media = []
                post['media'] = media
            else:
                post['media'] = []
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Posts not found"
        )
    return feed


@router.post("/feed", tags=["posts"], response_model=APIResponse)
async def create_post(post: PostCreate = Body(..., embed=True)):
    """
    Add new post if authorized
    """
    if FeedRepository.con is None:
        await DB.connect_db()
    user = await get_user_by_token(post.access_token)
    post_id = await FeedRepository.create_post(user['id'], post.title, post.message)
    if post_id is not False:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=f"Post(id={post_id}) has been created!"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post hasn't been created"
        )


@router.put("/feed/{post_id}/media", tags=["posts"], response_model=APIResponse)
async def upload_media_to_post(media: List[UploadFile], post_id: int, access_token: str = Body(..., embed=True)):
    """
    upload media to post if authorized
    """
    user = await get_user_by_token(access_token)
    await is_user_post(user['id'], post_id)
    res = await MediaRepository.add_all_media(post_id, user['id'], media)
    if res:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content="Media has been added to post"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed, try again later"
        )


@router.put("/feed/{post_id}", tags=["posts"], response_model=APIResponse)
async def update_post_message_and_title(post_id: int, post: PostCreate = Body(..., embed=True)):
    """
    update message and title int the post if authorized
    """
    user = await get_user_by_token(post.access_token)
    await is_user_post(user['id'], post_id)
    res = await FeedRepository.update_post_message_title(post_id, post.message, post.title)
    if res:
        return {'status_code': status.HTTP_200_OK, 'content': 'Post info has been successfully updated'}
    else:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail='Failed, try again later'
        )


@router.post("/feed/{post_id}/like", tags=["posts"], response_model=APIResponse)
async def like_post(post_id: int, access_token: str = Body(..., embed=True)):
    """
    put a like to post if authorized
    """
    if FeedRepository.con is None:
        await DB.connect_db()
    user = await get_user_by_token(access_token)
    await is_existed_post(post_id)
    is_liked = await LikeRepository.like_post(user['id'], post_id)
    if is_liked is True:
        return {'status_code': status.HTTP_200_OK, 'content': 'You liked post'}
    else:
        HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed, try again later"
        )


@router.post("/feed/{post_id}/unlike", tags=["posts"], response_model=APIResponse)
async def unlike_post(post_id: int, access_token: str = Body(..., embed=True)):
    """
    remove like from post if authorized
    """
    if FeedRepository.con is None:
        await DB.connect_db()
    user = await get_user_by_token(access_token)
    await is_existed_post(post_id)
    is_unliked = await LikeRepository.unlike_post(user['id'], post_id)
    if is_unliked is True:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content="You unliked post"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed, try again later"
        )
