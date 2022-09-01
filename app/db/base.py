import datetime
import os
import shutil
from typing import List

import asyncpg
from fastapi import UploadFile
from sqlalchemy import create_engine, MetaData, Enum
from databases import Database
from sqlalchemy.ext.declarative import declarative_base

from app.config import DATABASE_URL, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, HOST
from app.db import models

db = Database(DATABASE_URL)
metadata = MetaData()
engine = create_engine(DATABASE_URL)
Base = declarative_base()


class Tables(Enum):
    Users = 'aesn_users'
    Feed = 'aesn_feed'
    Media = 'aesn_media'
    Likes = 'aesn_likes'
    Tokens = 'aesn_tokens'


class DB:
    con: asyncpg.connection.Connection = None

    @classmethod
    async def connect_db(cls) -> bool:
        """
        Connect to database or create new database by models
        :return: True or False
        """
        try:
            url = os.environ.get('DATABASE_URL')
            if url:
                cls.con = await asyncpg.connect(url)
            else:
                cls.con = await asyncpg.connect(database=DATABASE_NAME, user=DATABASE_USER,
                                                password=DATABASE_PASSWORD, host=HOST, port=DATABASE_PORT)
        except Exception as er:
            print(er)
            cls.con = None
            return False
        if not await cls.connect_table(Tables.Users, models.User):
            return False
        if not await cls.connect_table(Tables.Feed, models.Post):
            return False
        if not await cls.connect_table(Tables.Likes, models.Likes):
            return False
        if not await cls.connect_table(Tables.Media, models.Media):
            return False
        return True

    @classmethod
    async def connect_table(cls, table_name, model):
        """
        connect to a table in db, create a new one by the model if table not exist
        :param table_name:
        :param model:
        :return:
        """
        try:
            a = await cls.con.fetch('select exists(select * from information_schema.tables where table_name = $1)',
                                    table_name)
        except Exception as er:
            print(er)
            await cls.con.close()
            return False
        if not a[0][0]:
            try:
                model.__table__.create(engine)
            except Exception as er:
                print(er)
                await cls.con.close()
                return False
        return True

    @classmethod
    async def disconnect_db(cls):
        """
        disconnect from database
        :return: True or False
        """
        await cls.con.close()


class UserData(DB):

    @classmethod
    async def create_user(cls, login: str, password: str, first_name: str = '', last_name: str = ''):
        """
        create a new user(
        create a new user by login and password, if both or one of the values(first_name, last_name) hasn't used)
        :param login:
        :param password:
        :param first_name: to use also fill last_name value
        :param last_name: to use also fill first_name value
        :return: True or False
        """
        time = datetime.datetime.utcnow()
        if first_name == '' and last_name == '':
            first_name = 'Noname'
            last_name = 'User'
        sql = f'insert into {Tables.Users}(login,hash,first_name,last_name,created_at) values ($1,$2,$3,$4,$5);'
        try:
            return await DB.con.execute(sql, login, password, first_name, last_name, time)
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def delete_user_by_id(cls, user_id: int):
        """
        delete user
        :param user_id:
        :return: True or False
        """
        sql = f'delete from {Tables.Users} where id=$1;'
        try:
            return await cls.con.execute(sql, user_id)
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def get_user_by_id(cls, user_id: int):
        """
        get user by id
        :param user_id:
        :return: dict() or False
        """
        sql = f"select * from {Tables.Users} where id=$1"
        try:
            return dict(await cls.con.fetchrow(sql, user_id))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def get_user_by_login(cls, login: str):
        """
        get user by login
        :param login:
        :return: dict() or False
        """
        sql = f"select * from {Tables.Users} where login=$1"
        try:
            return dict(await cls.con.fetchrow(sql, login))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def update_data(cls, user_id: int, new_login: str = None, new_password: str = None):
        """
        update user's data
        :param new_login:  optional
        :param user_id:
        :param new_password: optional
        :return: True or False
        """
        if new_login is not None and new_password is not None:
            sql = f'update {Tables.Users} set hash=$1,login=$2 where id=$3'
            try:
                return await cls.con.execute(sql, new_password, new_login, user_id)
            except Exception as e:
                print(e)
                return False
        elif new_login is None:
            sql = f'update {Tables.Users} set hash=$1 where id=$2'
            try:
                return await cls.con.execute(sql, new_password, user_id)
            except Exception as e:
                print(e)
                return False
        else:
            sql = f'update {Tables.Users} set login=$1 where id=$2'
            try:
                return await cls.con.execute(sql, new_login, user_id)
            except Exception as e:
                print(e)
                return False

    @classmethod
    async def update_names(cls, user_id: int,  new_first_name: str = None, new_last_name: str = None):
        if new_first_name is not None and new_last_name is not None:
            sql = f'update {Tables.Users} set first_name=$1,last_name=$2 where id=$3'
            try:
                return await cls.con.execute(sql, new_first_name, new_last_name, user_id)
            except Exception as e:
                print(e)
                return False
        elif new_first_name is None:
            sql = f'update {Tables.Users} set last_name=$1 where id=$2'
            try:
                return await cls.con.execute(sql, new_last_name, user_id)
            except Exception as e:
                print(e)
                return False
        else:
            sql = f'update {Tables.Users} set first_name=$1 where id=$2'
            try:
                return await cls.con.execute(sql, new_first_name, user_id)
            except Exception as e:
                print(e)
                return False


class FeedData(DB):

    @classmethod
    async def create_post(cls, author_id: int, title: str, message: str, has_media: bool, media: List[UploadFile] | None):
        """
        add post to db
        :param media: Optional
        :param author_id:
        :param title:
        :param message:
        :param has_media:
        :return: True - success, False - post not created, None - post has been created but some/all media not added
        """
        if not has_media and message is not None and title is not None:
            sql = f'insert into {Tables.Feed}(author_id,title,message) values ($1,$2,$3);'
            try:
                return await cls.con.execute(sql, author_id, title, message)
            except Exception as e:
                print(e)
                return False
        elif has_media and message is not None and title is not None:
            sql = f'insert into {Tables.Feed}(author_id,title,message,has_media) values ($1,$2,$3,$4) returning id;'
            try:
                post_id = await cls.con.fetchval(sql, author_id, title, message, has_media)
            except Exception as e:
                print(e)
                return False
            if not post_id:
                return False
            if 0 < len(media) <= 10:
                is_executed = True
                for img in media:
                    uri = f'static/{post_id}.{os.path.splitext(img.filename)[1]}'
                    if img is not UploadFile:
                        is_executed = None
                        continue
                    data = img.file.read()
                    with open(uri, mode='wb+') as f:
                        f.write(data)
                    sql = f'insert into {Tables.Media}(author_id,post_id,uri,extension) values ($1,$2,$3,$4);'
                    try:
                        await cls.con.execute(sql, author_id, post_id, uri, type)
                    except Exception as e:
                        print(e)
                        is_executed = None
                return is_executed
            else:
                return None
        elif has_media:
            sql = f'insert into {Tables.Feed}(author_id,has_media) values ($1,$2) returning id;'
            try:
                post_id = await cls.con.fetchval(sql, author_id, has_media)
            except Exception as e:
                print(e)
                return False
            if 0 < len(media) <= 10:
                res = await MediaData.add_all_media(post_id, author_id, media)
                if not res:
                    return None
                return res
            else:
                return None

    @classmethod
    async def delete_post(cls, post_id: int):
        """
        delete post by id
        :param post_id:
        :return: True or False
        """
        sql = f'delete from {Tables.Media} where post_id=$1;'
        try:
            shutil.rmtree(f'static/{post_id}')
        except Exception as e:
            print(e)
        sql = f'delete from {Tables.Feed} where id=$1;'
        try:
            return await cls.con.execute(sql, post_id)
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def delete_user_posts(cls, user_id: int):
        posts = await cls.get_user_posts(user_id)
        if isinstance(posts, list):
            for post in posts:
                await cls.delete_post(post['id'])

    @classmethod
    async def get_post_by_id(cls, post_id: int):
        """
        get post by id
        :param post_id:
        :return: dict() or False
        """
        sql = f"select * from {Tables.Feed} where id=$1"
        try:
            return dict(await cls.con.fetchrow(sql, post_id))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def get_user_posts(cls, user_id: int):
        sql = f"select * from {Tables.Feed} where author_id=$1"
        try:
            res = await cls.con.fetch(sql, user_id)
            return list(map(list, res))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def get_posts(cls, limit: int, page: int = 1):
        offset = page * limit
        sql = f'select * from {Tables.Feed} limit $1 offset $2'
        try:
            res = await cls.con.fetch(sql, limit, offset)
            return list(map(list, res))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def get_recommended_posts(cls, user_id: int, limit: int = 10):
        sql = f'select * from {Tables.Feed} where author_id!=$1 order by random() limit $2'
        try:
            res = await cls.con.fetch(sql, user_id, limit)
            return list(map(list, res))
        except Exception as e:
            print(e)
            return False


class LikeData(DB):

    @classmethod
    async def like_post(cls, user_id: int, post_id: int):
        """
        add like to a post from the user
        :param user_id:
        :param post_id:
        :return: True or False
        """
        sql = f'insert into {Tables.Likes}(user_id,post_id) values ($1,$2);'

        try:
            await cls.con.execute(sql, user_id, post_id)
        except Exception as e:
            print(e)
            return False

        liked_data = await LikeData.get_liked_posts(user_id, post_id)
        if liked_data is list:
            count = len(liked_data)
            sql = f'update {Tables.Feed} set likes=$1 where id=$2;'

            try:
                await cls.con.execute(sql, count, post_id)
            except Exception as e:
                print(e)
                return True

    @classmethod
    async def get_liked_posts(cls, user_id: int, post_id: int):
        """
        get all posts that user liked
        :param post_id:
        :param user_id:
        :return: list() or False
        """
        sql = f'select * from {Tables.Likes} where user_id=$1 and post_id=$2'
        try:
            res = await cls.con.fetch(sql, user_id, post_id)
            return list(map(list, res))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def get_liked_media(cls, user_id: int, media_id: int):
        """
        get all media that user liked
        :param media_id:
        :param user_id:
        :return: list() or False
        """
        sql = f'select * from {Tables.Likes} where user_id=$1 and media_id=$2'
        try:
            res = await cls.con.fetch(sql, user_id, media_id)
            return list(map(list, res))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def like_media(cls, user_id: int, media_id: int):
        """
        add like to the media from the user
        :param user_id:
        :param media_id:
        :return: True or False
        """
        sql = f'insert into {Tables.Likes}(user_id,media_id) values ($1,$2);'

        try:
            await cls.con.execute(sql, user_id, media_id)
        except Exception as e:
            print(e)
            return False

        liked_data = await LikeData.get_liked_media(user_id, media_id)
        if liked_data is list:
            count = len(liked_data)
            sql = f'update {Tables.Media} set likes=$1 where id=$2;'

            try:
                await cls.con.execute(sql, count, media_id)
            except Exception as e:
                print(e)
                return True

    @classmethod
    async def unlike_post(cls, user_id: int, post_id: int):
        """
        remove user's like from the post
        :param user_id:
        :param post_id:
        :return: True or False
        """
        sql = f'delete from {Tables.Likes} where user_id=$1 and post_id=$2;'
        try:
            await cls.con.execute(sql, user_id, post_id)
        except Exception as e:
            print(e)
            return False
        liked_data = await LikeData.get_liked_posts(user_id, post_id)
        if liked_data is list:
            count = len(liked_data)
            sql = f'update {Tables.Feed} set likes=$1 where id=$2;'

            try:
                await cls.con.execute(sql, count, post_id)
            except Exception as e:
                print(e)
                return True

    @classmethod
    async def unlike_media(cls, user_id: int, media_id: int):
        """
        remove user's like from the media
        :param user_id:
        :param media_id:
        :return: True or False
        """
        sql = f'delete from {Tables.Likes} where user_id=$1 and media_id=$2;'
        try:
            await cls.con.execute(sql, user_id, media_id)
        except Exception as e:
            print(e)
            return False
        liked_data = await LikeData.get_liked_media(user_id, media_id)
        if liked_data is list:
            count = len(liked_data)
            sql = f'update {Tables.Media} set likes=$1 where id=$2;'

            try:
                await cls.con.execute(sql, count, media_id)
            except Exception as e:
                print(e)
                return True


class MediaData(DB):

    @classmethod
    async def add_media(cls, author_id: int, post_id: int, media: UploadFile, i: int):
        uri = f'static/{post_id}/{i}.{os.path.splitext(media.filename)[1]}'
        if media is not UploadFile:
            return False
        data = media.file.read()
        with open(uri, mode='wb+') as f:
            f.write(data)
        sql = f'insert into {Tables.Media}(author_id,post_id,uri,extension) values ($1,$2,$3,$4);'
        try:
            await cls.con.execute(sql, author_id, post_id, uri, type)
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def add_all_media(cls, post_id: int, author_id: int, data: List[UploadFile]):
        media_i = 0
        is_added = True
        for media in data:
            media_i += 1
            if not cls.add_media(author_id, post_id, media, media_i):
                is_added = False
        return is_added

    @classmethod
    async def get_post_media(cls, post_id: int):
        sql = f'select * from {Tables.Media} where post_id=$1;'

        try:
            res = await cls.con.fetch(sql, post_id)
            return list(map(list, res))
        except Exception as e:
            print(e)
            return False

