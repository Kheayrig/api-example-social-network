import datetime

from fastapi import HTTPException, status

from app.db.base import DB


class FeedRepository(DB):
    table_name: str = 'aesn_feed'

    @classmethod
    async def create_post(cls, author_id: int, title: str, message: str):
        """
        add post to db
        :param author_id:
        :param title:
        :param message:
        :return: Id - success
        """
        time = datetime.datetime.utcnow()
        count = 0
        if message is not None and title is not None:
            sql = f'insert into {cls.table_name}(author_id,title,message,media_count,likes,created_at,updated_at)' \
                  f' values ($1,$2,$3,$4,$5,$6,$7) returning id'
            return await cls.con.fetchval(sql, author_id, title, message, count, count, time, time)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Not all fields filled'
            )

    @classmethod
    async def get_post_by_id(cls, post_id: int):
        """
        get post by id
        :param post_id:
        :return: dict()
        """
        sql = f"select * from {cls.table_name} where id=$1"
        res = await cls.con.fetchrow(sql, post_id)
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Post not found'
            )
        return dict(res)

    @classmethod
    async def get_user_posts(cls, user_id: int):
        """
        get all user's posts
        :param user_id:
        :return: list()
        """
        sql = f"select * from {cls.table_name} where author_id=$1"
        res = await cls.con.fetch(sql, user_id)
        if len(res) == 0:
            return []
        return list(map(dict, res))

    @classmethod
    async def get_posts(cls, limit: int = 10, page: int = 1):
        """
        get posts by limit with paging
        :param limit: optional, default = 10
        :param page: optional
        :return: list()
        """
        offset = page * limit
        sql = f'select * from {cls.table_name} limit $1 offset $2'
        res = await cls.con.fetch(sql, limit, offset)
        if len(res) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Posts not found'
            )
        return list(map(dict, res))

    @classmethod
    async def get_recommended_posts(cls, limit: int = 10):
        """
        get recommended posts order by likes (desc)
        :param limit: optional, default = 10
        :return: list()
        """
        sql = f'select * from {cls.table_name} order by likes desc limit $1'
        res = await cls.con.fetch(sql, limit)
        if len(res) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Posts not found'
            )
        return list(map(dict, res))

    @classmethod
    async def update_post_message_title(cls, post_id: int, new_message: str = None, new_title: str = None):
        """
        update post's message and/or title
        :param post_id:
        :param new_message:
        :param new_title:
        :return:
        """
        sql = f'update {cls.table_name} set title=$1,message=$2 where id=$3'
        await cls.con.execute(sql, new_title, new_message, post_id)

