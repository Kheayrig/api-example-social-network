from app.db.base import Tables, DB


class LikeRepository(DB):

    @classmethod
    async def like_post(cls, user_id: int, post_id: int):
        """
        add like to post from user
        :param user_id:
        :param post_id:
        :return: True or False
        """
        is_liked = await cls.check_if_liked(user_id, post_id)
        if is_liked:
            return True

        sql = f'insert into {Tables.Likes}(user_id,post_id) values ($1,$2);'

        try:
            await cls.con.execute(sql, user_id, post_id)
        except Exception as e:
            print(e)
            return False
        await cls.update_like_info(post_id)
        return True

    @classmethod
    async def unlike_post(cls, user_id: int, post_id: int):
        """
        remove user's like from post
        :param user_id:
        :param post_id:
        :return: True or False
        """
        is_liked = await cls.check_if_liked(user_id, post_id)
        if not is_liked:
            return True

        sql = f'delete from {Tables.Likes} where user_id=$1 and post_id=$2;'
        try:
            await cls.con.execute(sql, user_id, post_id)
        except Exception as e:
            print(e)
            return False

        await cls.update_like_info(post_id)
        return True

    @classmethod
    async def check_if_liked(cls, user_id: int, post_id: int):
        """
        check if post has already liked by user
        :param post_id:
        :param user_id:
        :return: True or False
        """
        sql = f'select * from {Tables.Likes} where user_id=$1 and post_id=$2'
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
        :return: list() or False
        """
        sql = f'select * from {Tables.Likes} where post_id=$1'
        try:
            res = await cls.con.fetch(sql, post_id)
            return list(map(dict, res))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def update_like_info(cls, post_id: int):
        """
        updated on the post's likes count
        :param post_id:
        :return:
        """
        liked_data = await LikeRepository.get_likes(post_id)
        count = len(liked_data)
        sql = f'update {Tables.Feed} set likes=$1 where id=$2;'

        try:
            await cls.con.execute(sql, count, post_id)
        except Exception as e:
            print(e)
