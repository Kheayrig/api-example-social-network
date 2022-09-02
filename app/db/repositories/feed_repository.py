import datetime

from app.db.base import Tables, DB
from app.db.repositories.like_repository import LikeRepository


class FeedRepository(DB):

    @classmethod
    async def create_post(cls, author_id: int, title: str, message: str):
        """
        add post to db
        :param author_id:
        :param title:
        :param message:
        :return: Id - success, False - post not created
        """
        time = datetime.datetime.utcnow()
        if message is not None and title is not None:
            sql = f'insert into {Tables.Feed}(author_id,title,message,created_at,updated_at) values ($1,$2,$3,$4,$5)' \
                  f' returning id;'
            try:
                return await cls.con.fetchval(sql, author_id, title, message, time, time)
            except Exception as e:
                print(e)
                return False
        else:
            return False

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
        """
        get all user's posts
        :param user_id:
        :return: list() or False
        """
        sql = f"select * from {Tables.Feed} where author_id=$1"
        try:
            res = await cls.con.fetch(sql, user_id)
            return list(map(dict, res))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def get_posts(cls, limit: int = 10, page: int = 1):
        """
        get posts by limit with paging
        :param limit: optional, default = 10
        :param page: optional
        :return: list() or False
        """
        offset = page * limit
        sql = f'select * from {Tables.Feed} limit $1 offset $2'
        try:
            res = await cls.con.fetch(sql, limit, offset)
            return list(map(dict, res))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def get_recommended_posts(cls, limit: int = 10):
        """
        get recommended posts order by likes (desc)
        :param limit: optional, default = 10
        :return: list() or False
        """
        sql = f'select * from {Tables.Feed} order by likes desc limit $1'
        try:
            res = await cls.con.fetch(sql, limit)
            return list(map(dict, res))
        except Exception as e:
            print(e)
            return False

