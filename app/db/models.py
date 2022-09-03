from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, String, Text, Enum,
)
import datetime

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Post(Base):
    __tablename__ = 'aesn_feed'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    author_id = Column(Integer, ForeignKey('aesn_users.id'), primary_key=True)
    title = Column(String, default='')
    message = Column(Text, default='')
    media_count = Column(Integer, default=0, nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __str__(self):
        return f'[{self.id}]{self.message}'


class User(Base):
    __tablename__ = 'aesn_users'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    email = Column(String, primary_key=True, unique=True)
    login = Column(String, primary_key=True, unique=True)
    hash = Column(String)
    first_name = Column(String, default='Noname')
    last_name = Column(String, default='User')
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class Media(Base):
    __tablename__ = 'aesn_media'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    author_id = Column(Integer, ForeignKey('aesn_users.id'))
    post_id = Column(Integer, ForeignKey('aesn_feed.id'))
    uri = Column(String, nullable=False, primary_key=True)
    extension = Column(String, default='.png')
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Likes(Base):
    __tablename__ = 'aesn_likes'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = Column(Integer, ForeignKey('aesn_users.id'))
    post_id = Column(Integer, ForeignKey('aesn_feed.id'))
    media_id = Column(Integer, ForeignKey('aesn_media.id'))
