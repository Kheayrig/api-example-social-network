import datetime
import os
import shutil
from typing import List
from fastapi import UploadFile, HTTPException, status

from app.config import DATA_PATH
from app.db.base import DB
from app.db.repositories.feed_repository import FeedRepository
from app.utils.log_settings import log


class MediaRepository(DB):
    table_name: str = 'aesn_media'

    @classmethod
    async def add_media(cls, author_id: int, post_id: int, media: UploadFile, i: int, part_uri: str):
        """
        add a media file to post
        :param part_uri:
        :param author_id:
        :param post_id:
        :param media:
        :param i:
        :return:
        """
        extension = os.path.splitext(media.filename)[1]
        uri = part_uri + f'/{i}{extension}'

        data = media.file.read()
        with open(uri, mode='wb+') as f:
            f.write(data)

        created_at = datetime.datetime.utcnow()
        sql = f'insert into {cls.table_name}(author_id,post_id,uri,extension,likes,created_at) values ($1,$2,$3,$4,$5,$6)'
        await cls.con.execute(sql, author_id, post_id, uri, extension, 0, created_at)

    @classmethod
    async def del_post_media(cls, post_id: int):
        part_uri = DATA_PATH + f"{post_id}"
        if os.path.exists(part_uri):
            shutil.rmtree(part_uri)
            os.mkdir(part_uri)
        data = await cls.get_post_media(post_id)
        if len(data) > 0:
            sql = f'delete from {cls.table_name} where id=$1'
            for media in data:
                await cls.con.execute(sql, media['id'])

    @classmethod
    async def add_all_media(cls, post_id: int, author_id: int, data: List[UploadFile]):
        """
        add all sent media to a post
        :param post_id:
        :param author_id:
        :param data:
        :return:
        """
        if 0 < len(data) <= 10:
            part_uri = DATA_PATH + f"{post_id}"
            await cls.del_post_media(post_id)
            os.mkdir(part_uri)
            media_i = 0
            for media in data:
                media_i += 1
                await cls.add_media(author_id, post_id, media, media_i, part_uri)
            await cls.update_media_count(post_id)
            return
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Media count has to be more than 0 and less than 11'
        )

    @classmethod
    async def get_post_media(cls, post_id: int):
        """
        get all post's media
        :param post_id:
        :return: list()
        """
        sql = f'select * from {cls.table_name} where post_id=$1'

        res = await cls.con.fetch(sql, post_id)
        if len(res) == 0:
            return []
        return list(map(dict, res))

    @classmethod
    async def update_media_count(cls, post_id):
        """
        update media count variable in post
        :param post_id:
        :return:
        """
        path_post_media = DATA_PATH + f"{post_id}"
        count = len(os.listdir(path_post_media))
        sql = f'update {FeedRepository.table_name} set media_count=$1 where id=$2'

        try: 
            await cls.con.execute(sql, count, post_id)
        except Exception as e:
            log.warn(e, exc_info=True)
