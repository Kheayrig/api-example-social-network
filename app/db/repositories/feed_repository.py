import datetime

from app.db.base import Tables, DB


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
            sql = f'insert into {Tables.Feed}(author_id,title,message,media_count,likes,created_at,updated_at)' \
                  f' values ($1,$2,$3,$4,$5,$6) returning id;'
            try:
                return await cls.con.fetchval(sql, author_id, title, message, 0, 0, time, time)
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

    @classmethod
    async def update_post_message_title(cls, post_id: int, new_message: str = None, new_title: str = None):
        """
        update post's message and/or title
        :param post_id:
        :param new_message:
        :param new_title:
        :return: True or False
        """
        sql = f'update {Tables.Feed} set title=$1,message=$2 where id=$3'
        try:
            return await cls.con.execute(sql, new_title, new_message, post_id)
        except Exception as e:
            print(e)
            return False

