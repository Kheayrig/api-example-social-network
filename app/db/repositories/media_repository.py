import datetime
import os
import shutil
from typing import List
from fastapi import UploadFile

from app.config import DATA_PATH
from app.db.base import Tables, DB


class MediaRepository(DB):

    @classmethod
    async def add_media(cls, author_id: int, post_id: int, media: UploadFile, i: int, part_uri: str):
        """
        add a media file to post
        :param part_uri:
        :param author_id:
        :param post_id:
        :param media:
        :param i:
        :return: True or False
        """
        extension = os.path.splitext(media.filename)[1]
        uri = part_uri + f'/{i}{extension}'
        try:
            data = media.file.read()
            with open(uri, mode='wb+') as f:
                f.write(data)
        except Exception as e:
            print(e)
            return False

        created_at = datetime.datetime.utcnow()
        sql = f'insert into {Tables.Media}(author_id,post_id,uri,extension,likes,created_at) values ($1,$2,$3,$4,$5,$6);'
        try:
            return await cls.con.execute(sql, author_id, post_id, uri, extension, 0, created_at)
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def add_all_media(cls, post_id: int, author_id: int, data: List[UploadFile]):
        """
        add all sent media to a post
        :param post_id:
        :param author_id:
        :param data:
        :return: True - success, None - not all media added, False - failed
        """
        if 0 < len(data) <= 10:
            part_uri = DATA_PATH + f"{post_id}"
            if not os.path.exists(part_uri):
                os.mkdir(part_uri)
            else:
                shutil.rmtree(part_uri)
                os.mkdir(part_uri)
            media_i = 0
            is_added = True
            for media in data:
                media_i += 1
                res = await cls.add_media(author_id, post_id, media, media_i, part_uri)
                if not res:
                    is_added = None
            await cls.update_media_count(post_id)
            return is_added
        return False

    @classmethod
    async def get_post_media(cls, post_id: int):
        """
        get all post's media
        :param post_id:
        :return: list() or False
        """
        sql = f'select * from {Tables.Media} where post_id=$1;'

        try:
            res = await cls.con.fetch(sql, post_id)
            return list(map(dict, res))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def get_media(cls):
        """
        get all post's media
        :return: list() or False
        """
        sql = f'select * from {Tables.Media}'

        try:
            res = await cls.con.fetch(sql)
            return list(map(UploadFile, res))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def update_media_count(cls, post_id):
        """
        update media count variable in post
        :param post_id:
        :return:
        """
        path_post_media = DATA_PATH + f"{post_id}"
        count = len(os.listdir(path_post_media))
        sql = f'update {Tables.Feed} set media_count=$1 where id=$2;'

        try:
            await cls.con.execute(sql, count, post_id)
        except Exception as e:
            print(e)
