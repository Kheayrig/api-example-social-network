import os
from pathlib import Path

from starlette.config import Config

config = Config('.env')

ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = 'HS256'
SECRET_KEY = 'aerfudiohkj439uji43kfu8oi32f9jo3r29j0dej09w23rewafzds'

# data_path
"""
path to media storage
"""
path = os.path.join(str(Path.cwd()), 'static')
DATA_PATH = config('DATA_PATH', cast=str, default=path)

# database
DATABASE_URL = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
DATABASE_NAME = config('DATABASE_NAME', cast=str, default='d2fd31b8df7gta')
DATABASE_USER = config('DATABASE_USER', cast=str, default='utfpmtzzdxbdi')
DATABASE_PASSWORD = config('DATABASE_PASSWORD', cast=str, default='c0575207ea21666604d6d2ab1344b2ed203cc46aaad234929f1863b5a03fe2dd')
DATABASE_PORT = config('DATABASE_PORT', cast=str, default='5432')
DATABASE_HOST = config('DATABASE_HOST', cast=str, default='ec2-107-23-76-12.compute-1.amazonaws.com')
