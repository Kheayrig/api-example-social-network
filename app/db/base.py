import asyncpg
from fastapi import HTTPException, status

from app.config import DATABASE_URL
from app.utils.create_db import add_all_tables


class DB:
    con: asyncpg.connection.Connection = None
    tablesCount: int = 4

    @staticmethod
    def format_fields(*args):
        return ','.join(args)

    @classmethod
    async def connect_db(cls):
        """
        Connect to database or create new database by repositories
        :return: True or False
        """
        try:
            cls.con = await asyncpg.connect(DATABASE_URL)
        except Exception as er:
            cls.con = None
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail='Connection to database is failed'
            )
        await cls.connect_tables()

    @classmethod
    async def connect_tables(cls):
        """
        connect to tables in db, create if found 0, else raise ConnectionRefusedError
        :return: True, False, ConnectionRefusedError
        """
        try:
            a = await cls.con.fetch("select table_name from information_schema.tables where table_schema='public'")
        except Exception as er:
            await cls.disconnect_db()
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail='Connection to database is failed'
            )
        if len(a) != cls.tablesCount:
            try:
                add_all_tables(DATABASE_URL)
            except Exception as er:
                await cls.disconnect_db()
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail='Connection to tables is failed'
                )

    @classmethod
    async def disconnect_db(cls):
        """
        disconnect from database
        :return:
        """
        await cls.con.close()
