import datetime

from fastapi import HTTPException, status

from app.db.base import DB


class FeedRepository(DB):
    table_name: str = 'aesn_feed'
    id = 'id'
    author_id = 'author_id'
    title = 'title'
    message = 'message'
    media_count = 'media_count'
    likes = 'likes'
    created_at = 'created_at'
    updated_at = 'updated_at'

    @classmethod
    async def create_post(cls, author_id: int, title: str, message: str):
        """
        add post to db
        :param author_id:
        :param title:
        :param message:
        :return: ID of new post
        """
        time = datetime.datetime.utcnow()
        count = 0
        create_fields = cls.format_fields(cls.author_id, cls.title, cls.message, cls.media_count, cls.likes,
                                          cls.created_at, cls.updated_at)
        sql = f'insert into {cls.table_name}({create_fields})' \
              f' values ($1,$2,$3,$4,$5,$6,$7) returning {cls.id}'
        res = await cls.con.fetchval(sql, author_id, title, message, count, count, time, time)
        return res

    @classmethod
    async def delete_post(cls, post_id: int):
        """
        delete post without media by id
        :param post_id:
        :return:
        """
        sql = f'delete from {cls.table_name} where {cls.id}=$1'
        await cls.con.execute(sql, post_id)

    @classmethod
    async def get_post(cls, value: int, field: str = 'id', fields: str = '*'):
        """
        get post by value
        :param value:
        :param field:
        :param fields: return fields of post
        :return: dict()
        """
        sql = f"select {fields} from {cls.table_name} where {field}=$1"
        res = await cls.con.fetchrow(sql, value)
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Post not found'
            )
        return dict(res)

    @classmethod
    async def get_user_posts(cls, user_id: int, fields: str = '*'):
        """
        get all user's posts
        :param user_id:
        :param fields:
        :return: list()
        """
        sql = f"select {fields} from {cls.table_name} where {cls.author_id}=$1"
        res = await cls.con.fetch(sql, user_id)
        if len(res) == 0:
            return []
        return list(map(dict, res))

    @classmethod
    async def get_posts(cls, limit: int = 10, page: int = 0, fields: str = '*'):
        """
        get posts by limit with paging
        :param limit: optional, default = 10
        :param page: optional
        :param fields:
        :return: list()
        """
        offset = page * limit
        sql = f'select {fields} from {cls.table_name} limit $1 offset $2'
        res = await cls.con.fetch(sql, limit, offset)
        if len(res) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Posts not found'
            )
        return list(map(dict, res))

    @classmethod
    async def get_recommended_posts(cls, limit: int = 10, fields: str = '*'):
        """
        get recommended posts order by likes (desc)
        :param limit: optional, default = 10
        :param fields:
        :return: list()
        """
        sql = f'select {fields} from {cls.table_name} order by {cls.likes} desc limit $1'
        res = await cls.con.fetch(sql, limit)
        if len(res) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Posts not found'
            )
        return list(map(dict, res))

    @classmethod
    async def update_post(cls, post_id: int, data: dict):
        """
        update post's message and/or title
        :param post_id:
        :param data: dict of values for updating in the format (field:value)
        :return:
        """
        i = 1
        args = []
        data[cls.updated_at] = datetime.datetime.utcnow()
        for field in data:
            args.append(f'{field}=${i}')
            i += 1
        sql = f'update {cls.table_name} set {DB.format_fields(*args)} where {cls.id}=${i}'
        await cls.con.execute(sql, *data.values(), post_id)

    @classmethod
    async def is_existed_post(cls, post_id: int, field: str = "id"):
        sql = f"select exists(select 1 from {cls.table_name} where {field}=$1)"
        res = await cls.con.fetchval(sql, post_id)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

