import datetime
from typing import Optional, List

from fastapi import Header, UploadFile
from pydantic import BaseModel, EmailStr, constr, Field


class UserIn(BaseModel):
    login: Optional[str]
    password: Optional[constr(min_length=8)]


class Profile(UserIn):
    first_name: Optional[str] = Field(None, min_length=2, max_length=35,
                            regex=r'^([^0-9!\@#$%^&(),.+=/\\{}\[\]?><":;|]*)$')
    last_name: Optional[str] = Field(None, min_length=2, max_length=35,
                           regex=r'^([^0-9!\@#$%^&(),.+=/\\{}\[\]?><":;|]*)$')


class UserCreate(UserIn):
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""


class Token(BaseModel):
    login: str


class BaseFeed(BaseModel):
    title: str
    message: str
    has_media: bool
    likes: int


class Media(BaseModel):
    id: str
    author_id: str
    post_id: str
    uri: str
    extension: str
    likes: int
    created_at: datetime.datetime


class Feed(BaseFeed):
    id: Optional[str] = None
    author_id: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    media: List[Media]


class PostCreate(BaseModel):
    access_token: str
    title: str
    message: str
    has_media: bool = False


class User(BaseModel):
    id: Optional[str] = None
    login: Optional[str] = None
    hash: Optional[str] = None
    first_name: Optional[str] = Field(None, min_length=2, max_length=35,
                                      regex=r'^([^0-9!\@#$%^&(),.+=/\\{}\[\]?><":;|]*)$')
    last_name: Optional[str] = Field(None, min_length=2, max_length=35,
                                     regex=r'^([^0-9!\@#$%^&(),.+=/\\{}\[\]?><":;|]*)$')
    created_at: datetime.datetime
