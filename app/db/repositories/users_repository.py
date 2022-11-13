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
    create = DB.fields(login, hash, first_name, last_name, created_at)
    update = DB.fields(login, hash, first_name, last_name)

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
        sql = f'insert into {cls.table_name}({cls.create}) values ($1,$2,$3,$4,$5)'
        await DB.con.execute(sql, login, password, first_name, last_name, time)

    @classmethod
    async def delete_user(cls, value, field: str = id):
        """
        delete user by field
        :param field:
        :param value:
        :return:
        """
        sql = f"delete from {cls.table_name} where {field}=$1"
        await cls.con.execute(sql, value)

    @classmethod
    async def get_user(cls, value, value_field: str = id, fields: str = '*') -> dict:
        """
        get user by value
        :param value:
        :param value_field:
        :param fields:
        :return: dict()
        """
        sql = f"select {fields} from {cls.table_name} where {value_field}=$1"
        res = await cls.con.fetchrow(sql, value)
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        return res

    @classmethod
    async def is_user_existed(cls, field: str, login: str = '', user_id: int = 0):
        """
        check if user exists by login or id
        :param field:
        :param login:
        :param user_id: optional
        :return: user exist: nothing; user not exist: HTTPException(401)
        """
        sql = f"select exists(select 1 from {cls.table_name} where {field}=$1)"
        res = await cls.con.fetchval(sql, login if field == cls.login else user_id)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login not unique",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @classmethod
    async def update_data(cls, user_id: int, fields: dict):
        """
        update user's login and/or password
        :param user_id:
        :param fields: dict of values for updating in the format (field:value)
        :return:
        """
        i = 1
        args = []
        for field in fields:
            args.append(f'{field}=${i}')
            i += 1
        sql = f'update {cls.table_name} set {DB.fields(*args)} where id=${i}'
        await cls.con.execute(sql, *fields.values(), user_id)
