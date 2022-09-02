import datetime

from app.db.base import DB, Tables


class UserRepository(DB):

    @classmethod
    async def create_user(cls, login: str, password: str, first_name: str = None, last_name: str = None):
        """
        create a new user(
        create a new user only by login and password, if both or one of the values(first_name, last_name) hasn't used)
        :param login:
        :param password:
        :param first_name: to use also fill last_name value
        :param last_name: to use also fill first_name value
        :return: True or False
        """
        time = datetime.datetime.utcnow()
        if first_name is None and last_name is None:
            first_name = 'Noname'
            last_name = 'User'
        sql = f'insert into {Tables.Users}(login,hash,first_name,last_name,created_at) values ($1,$2,$3,$4,$5);'
        try:
            return await DB.con.execute(sql, login, password, first_name, last_name, time)
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def get_user_by_id(cls, user_id: int):
        """
        get user by id
        :param user_id:
        :return: dict() or False
        """
        sql = f"select * from {Tables.Users} where id=$1"
        try:
            return dict(await cls.con.fetchrow(sql, user_id))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def get_user_by_login(cls, login: str):
        """
        get user by login
        :param login:
        :return: dict() or False
        """
        sql = f"select * from {Tables.Users} where login=$1"
        try:
            return dict(await cls.con.fetchrow(sql, login))
        except Exception as e:
            print(e)
            return False

    @classmethod
    async def update_data(cls, user_id: int, new_login: str = None, new_password: str = None):
        """
        update user's login and/or password
        :param new_login:  optional
        :param user_id:
        :param new_password: optional
        :return: True or False
        """
        if new_login is not None and new_password is not None:
            sql = f'update {Tables.Users} set hash=$1,login=$2 where id=$3'
            try:
                return await cls.con.execute(sql, new_password, new_login, user_id)
            except Exception as e:
                print(e)
                return False
        elif new_password is not None:
            sql = f'update {Tables.Users} set hash=$1 where id=$2'
            try:
                return await cls.con.execute(sql, new_password, user_id)
            except Exception as e:
                print(e)
                return False
        elif new_login is not None:
            sql = f'update {Tables.Users} set login=$1 where id=$2'
            try:
                return await cls.con.execute(sql, new_login, user_id)
            except Exception as e:
                print(e)
                return False

    @classmethod
    async def update_names(cls, user_id: int, new_first_name: str = None, new_last_name: str = None):
        """
        update user's first or/and last names
        :param user_id:
        :param new_first_name: optional
        :param new_last_name: optional
        :return: True or False
        """
        if new_first_name is not None and new_last_name is not None:
            sql = f'update {Tables.Users} set first_name=$1,last_name=$2 where id=$3'
            try:
                return await cls.con.execute(sql, new_first_name, new_last_name, user_id)
            except Exception as e:
                print(e)
                return False
        elif new_last_name is not None:
            sql = f'update {Tables.Users} set last_name=$1 where id=$2'
            try:
                return await cls.con.execute(sql, new_last_name, user_id)
            except Exception as e:
                print(e)
                return False
        elif new_first_name is not None:
            sql = f'update {Tables.Users} set first_name=$1 where id=$2'
            try:
                return await cls.con.execute(sql, new_first_name, user_id)
            except Exception as e:
                print(e)
                return False
