import datetime
from typing import Optional, List
from pydantic import BaseModel, constr, Field


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Auth(BaseModel):
    login: Optional[str] = Field(min_length=4, max_length=20, regex=r'^[a-z0-9_-]+$')
    password: Optional[constr(min_length=8, max_length=128)]


class RegistrationForm(Auth):
    first_name: Optional[str] = Field(min_length=2, max_length=35,
                                      regex=r'^[A-Za-z]+((\s)?([A-Za-z])+)*$')
    last_name: Optional[str] = Field(min_length=2, max_length=35,
                                     regex=r'^[A-Za-z]+((\s)?([A-Za-z])+)*$')
    login: Optional[str] = Field(min_length=4, max_length=20, regex=r'^[a-z0-9_-]+$')


class User(BaseModel):
    id: Optional[str]
    first_name: Optional[str] = Field(min_length=2, max_length=35,
                                      regex=r'^[A-Za-z]+((\s)?([A-Za-z])+)*$')
    last_name: Optional[str] = Field(min_length=2, max_length=35,
                                     regex=r'^[A-Za-z]+((\s)?([A-Za-z])+)*$')
    login: Optional[str] = Field(min_length=4, max_length=20, regex=r'^[a-z0-9_-]+$')
    created_at: datetime.datetime


class ProfileSettings(BaseModel):
    first_name: Optional[str] = Field(min_length=2, max_length=35,
                                      regex=r'^[A-Za-z]+((\s)?([A-Za-z])+)*$')
    last_name: Optional[str] = Field(min_length=2, max_length=35,
                                     regex=r'^[A-Za-z]+((\s)?([A-Za-z])+)*$')
    login: Optional[str] = Field(min_length=4, max_length=20, regex=r'^[a-z0-9_-]+$')
    password: Optional[str] = Field(min_length=8, max_length=128)
    old_password: str = Field(min_length=8, max_length=128)


class Media(BaseModel):
    id: str
    author_id: str
    post_id: str
    uri: str
    extension: str
    likes: int
    created_at: datetime.datetime


class Feed(BaseModel):
    id: int
    title: str = None
    message: str = None
    media_count: int = None
    likes: int = 0
    author_id: Optional[str] = None
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None
    media: List[Media] = []


class PostCreate(BaseModel):
    title: str
    message: str


