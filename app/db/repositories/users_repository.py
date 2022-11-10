import datetime

from fastapi import HTTPException, status

from app.db.base import DB


class UserRepository(DB):
    table_name: str = 'aesn_users'
    id = 'id'
    login = 'login'
    hash = 'hash'
    first_name = 'first_name'
    last_name = 'last_name'
    created_at = 'created_at'
    all = DB.fields(id, login, hash, first_name, last_name, created_at)

    @classmethod
    async def create_user(cls, login: str, password: str, first_name: str = 'Noname', last_name: str = 'User'):
        """
        create a new user(
        create a new user only by login and password, if both or one of the values(first_name, last_name) hasn't used)
        :param login:
        :param password:
        :param first_name: to use also fill last_name value
        :param last_name: to use also fill first_name value
        :return:
        """
        await cls.is_user_existed(cls.login, login=login)
        time = datetime.datetime.utcnow()
        if first_name is None and last_name is None:
            first_name = 'Noname'
            last_name = 'User'
        sql = f'insert into {cls.table_name}({cls.fields}) values ($1,$2,$3,$4,$5)'
        await DB.con.execute(sql, login, password, first_name, last_name, time)

    @classmethod
    async def delete_user_by_id(cls, user_id: int):
        """
        delete user by id
        :param user_id:
        :return:
        """
        sql = f"delete from {cls.table_name} where {cls.id}=$1"
        await cls.con.execute(sql, user_id)

    @classmethod
    async def get_user_by_id(cls, user_id: int, fields: str = '*'):
        """
        get user by id
        :param user_id:
        :param fields:
        :return: dict()
        """
        sql = f"select {fields} from {cls.table_name} where {cls.id}=$1"
        res = await cls.con.fetchrow(sql, user_id)
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        return res

    @classmethod
    async def get_user_by_login(cls, login: str, fields: str = '*'):
        """
        get user by login
        :param login:
        :return: dict()
        """
        sql = f"select {fields} from {cls.table_name} where {cls.login}=$1"
        res = await cls.con.fetchrow(sql, login)
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        return res

    @classmethod
    async def is_user_existed(cls, field: str, login: str = '', id: int = 0):
        """
        check if user exists by login or id
        :param field:
        :param login:
        :param id: optional
        :return: user exist: nothing; user not exist: HTTPException(401)
        """
        sql = f"select exists(select 1 from {cls.table_name} where {field}=$1)"
        res = await cls.con.fetchval(sql, login if field == cls.login else id)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login not unique",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return

    @classmethod
    async def update_data(cls, user_id: int, new_login: str = None, new_password: str = None):
        """
        update user's login and/or password
        :param new_login:  optional
        :param user_id:
        :param new_password: optional
        :return:
        """
        if new_login is not None and new_password is not None:
            sql = f'update {cls.table_name} set {cls.hash}=$1,{cls.login}=$2 where id=$3'
            await cls.con.execute(sql, new_password, new_login, user_id)
        elif new_password is not None:
            sql = f'update {cls.table_name} set {cls.hash}=$1 where id=$2'
            await cls.con.execute(sql, new_password, user_id)
        elif new_login is not None:
            sql = f'update {cls.table_name} set {cls.login}=$1 where id=$2'
            await cls.con.execute(sql, new_login, user_id)

    @classmethod
    async def update_names(cls, user_id: int, new_first_name: str = None, new_last_name: str = None):
        """
        update user's first or/and last names
        :param user_id:
        :param new_first_name: optional
        :param new_last_name: optional
        :return:
        """
        if new_first_name is not None and new_last_name is not None:
            sql = f'update {cls.table_name} set {cls.first_name}=$1,{cls.last_name}=$2 where {cls.id}=$3'
            await cls.con.execute(sql, new_first_name, new_last_name, user_id)
        elif new_last_name is not None:
            sql = f'update {cls.table_name} set {cls.last_name}=$1 where {cls.id}=$2'
            await cls.con.execute(sql, new_last_name, user_id)
        elif new_first_name is not None:
            sql = f'update {cls.table_name} set {cls.first_name}=$1 where {cls.id}=$2'
            await cls.con.execute(sql, new_first_name, user_id)
