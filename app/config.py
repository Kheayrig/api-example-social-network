from starlette.config import Config

config = Config('.env')

HOST = config('DATABASE_HOST', cast=str, default='127.0.0.1')
PORT = config('PORT', cast=int, default=8000)

DATABASE_URL = config('AESN_DATABASE_URL', cast=str,
                      default='postgresql://postgres:root@localhost:32700/ae-social-network')
DATABASE_NAME = config('DATABASE_NAME', cast=str, default='ae-social-network')
DATABASE_USER = config('DATABASE_USER', cast=str, default='postgres')
DATABASE_PASSWORD = config('DATABASE_PASSWORD', cast=str, default='root')
DATABASE_PORT = config('DATABASE_PORT', cast=str, default='32700')

ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = 'HS256'
SECRET_KEY = 'aerfudiohkj439uji43kfu8oi32f9jo3r29j0dej09w23rewafzds'

DATA_PATH = config('DATA_PATH', cast=str, default=r'D:/static/')
