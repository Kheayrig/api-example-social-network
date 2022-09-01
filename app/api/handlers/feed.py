from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, Header, status, Body, File
from fastapi.responses import JSONResponse

from app.api.schema import Feed, Media, PostCreate
from app.api.security import get_current_user
from app.db.base import FeedData, MediaData, UserData, DB

router = APIRouter()


@router.get("/feed/{post_id}", response_model=Feed)
async def get_post(post_id: int):
    if FeedData.con is None:
        await DB.connect_db()
    feed = await FeedData.get_post_by_id(post_id)
    if isinstance(feed, dict):
        if feed['has_media'] is True:
            media = await MediaData.get_post_media(post_id)
            if media is False:
                media = []
            feed['media'] = media
        else:
            feed['media'] = []
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return feed


@router.get("/feed", response_model=List[Feed])
async def get_feed(limit: int = 0, page: int = 0):
    if FeedData.con is None:
        await DB.connect_db()
    feed = await FeedData.get_posts(limit, page)
    if isinstance(feed, list):
        for post in feed:
            if post['has_media'] is True:
                media = await MediaData.get_post_media(post['id'])
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


@router.post("/feed")
async def create_post(access_token: str, title: str, message: str, has_media: bool, media: UploadFile = File(...)):
    """
    Add new post if authorized
    """
    if FeedData.con is None:
        await DB.connect_db()
    print("start creating")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    jwt = get_current_user(access_token)
    if jwt.login is not None:
        user = await UserData.get_user_by_login(jwt.login)
        if isinstance(user, dict):
            is_created = await FeedData.create_post(user['id'], title, message, has_media, media)
            if is_created is True:
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content="Post has been created!"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Post hasn't been created"
                )
