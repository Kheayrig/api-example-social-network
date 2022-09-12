from app.db.base import DB
from app.db.repositories.feed_repository import FeedRepository
from fastapi import status, HTTPException


class LikeRepository(DB):
    table_name: str = 'aesn_likes'

    @classmethod
    async def like_post(cls, user_id: int, post_id: int):
        """
        add like to post from user
        :param user_id:
        :param post_id:
        :return:
        """
        is_liked = await cls.check_if_liked(user_id, post_id)
        if is_liked:
            return

        sql = f'insert into {cls.table_name}(user_id,post_id) values ($1,$2)'

        await cls.con.execute(sql, user_id, post_id)
        await cls.update_like_info(post_id)

    @classmethod
    async def unlike_post(cls, user_id: int, post_id: int):
        """
        remove user's like from post
        :param user_id:
        :param post_id:
        :return:
        """
        is_liked = await cls.check_if_liked(user_id, post_id)
        if not is_liked:
            return

        sql = f'delete from {cls.table_name} where user_id=$1 and post_id=$2'
        await cls.con.execute(sql, user_id, post_id)
        await cls.update_like_info(post_id)

    @classmethod
    async def check_if_liked(cls, user_id: int, post_id: int):
        """
        check if post has already liked by user
        :param post_id:
        :param user_id:
        :return: True or False
        """
        sql = f'select * from {cls.table_name} where user_id=$1 and post_id=$2'
        try:
            res = await cls.con.fetchrow(sql, user_id, post_id)
            if res is None:
                return False
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def get_likes(cls, post_id: int):
        """
        get all posts that user likes
        :param post_id:
        :return: list()
        """
        sql = f'select * from {cls.table_name} where post_id=$1'
        res = await cls.con.fetch(sql, post_id)
        if len(res) == 0:
            return []
        return list(map(dict, res))

    @classmethod
    async def update_like_info(cls, post_id: int):
        """
        updated on the post's likes count
        :param post_id:
        :return:
        """
        liked_data = await LikeRepository.get_likes(post_id)
        count = len(liked_data)
        sql = f'update {FeedRepository.table_name} set likes=$1 where id=$2'

        try:
            await cls.con.execute(sql, count, post_id)
        except Exception as e:
            print(e)
