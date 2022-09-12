import datetime
from typing import Optional, List

from pydantic import BaseModel, constr, Field
from starlette import status


class APIResponse(BaseModel):
    status_code: int = status.HTTP_200_OK
    content: str


class UserIn(BaseModel):
    login: Optional[str] = Field(min_length=4, max_length=20, regex=r'^[a-z0-9_-]+$')
    password: Optional[constr(min_length=8, max_length=128)]


class Profile(UserIn):
    first_name: Optional[str] = Field(min_length=2, max_length=35,
                            regex=r'^[A-Za-z]+((\s)?([A-Za-z])+)*$')
    last_name: Optional[str] = Field(min_length=2, max_length=35,
                           regex=r'^[A-Za-z]+((\s)?([A-Za-z])+)*$')


class ProfileSettings(Profile):
    old_password: Optional[constr(min_length=8, max_length=128)]


class BaseFeed(BaseModel):
    title: str
    message: str
    media_count: int
    likes: int
    id: Optional[str]
    author_id: Optional[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime


class Media(BaseModel):
    id: str
    author_id: str
    post_id: str
    uri: str
    extension: str
    likes: int
    created_at: datetime.datetime


class Feed(BaseFeed):
    media: List[Media]


class PostCreate(BaseModel):
    title: str
    message: str


class User(BaseModel):
    id: Optional[str]
    login: Optional[str] = Field(min_length=4, max_length=20, regex=r'^[a-z0-9_-]+$')
    first_name: Optional[str] = Field(min_length=2, max_length=35,
                                      regex=r'^[A-Za-z]+((\s)?([A-Za-z])+)*$')
    last_name: Optional[str] = Field(min_length=2, max_length=35,
                                     regex=r'^[A-Za-z]+((\s)?([A-Za-z])+)*$')
    created_at: datetime.datetime
