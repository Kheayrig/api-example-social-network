import os

import asyncpg
from sqlalchemy import create_engine, MetaData, Enum
from databases import Database

from app.config import DATABASE_URL, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST
from app.db import models

db = Database(DATABASE_URL)
metadata = MetaData()
engine = create_engine(DATABASE_URL)


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
        Connect to database or create new database by repositories
        :return: True or False
        """
        try:
            url = os.environ.get('DATABASE_URL')
            if url:
                cls.con = await asyncpg.connect(url)
            else:
                cls.con = await asyncpg.connect(database=DATABASE_NAME, user=DATABASE_USER,
                                                password=DATABASE_PASSWORD, host=DATABASE_HOST, port=DATABASE_PORT)
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
        :return: True or False
        """
        try:
            a = await cls.con.fetch('select exists(select * from information_schema.tables where table_name = $1)',
                                    table_name)
        except Exception as er:
            print(er)
            await cls.disconnect_db()
            return False
        if not a[0][0]:
            try:
                model.__table__.create(engine)
            except Exception as er:
                print(er)
                await cls.disconnect_db()
                return False
        return True

    @classmethod
    async def disconnect_db(cls):
        """
        disconnect from database
        :return:
        """
        await cls.con.close()
