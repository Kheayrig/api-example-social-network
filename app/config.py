import os
from pathlib import Path

from starlette.config import Config

config = Config('.env')
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = 'HS256'
# secret key for cash
SECRET_KEY = os.environ.get('SECRET_KEY', config('SECRET_KEY', cast=str, default=""))

# data_path
"""
path to media storage, if DATA_PATH not found -> use 'static' directory in root dir
"""
path = os.path.join(str(Path.cwd()), 'static')
DATA_PATH = config('DATA_PATH', cast=str, default=path)

# database
DATABASE_URL = os.environ.get('DATABASE_URL', config('DATABASE_URL', cast=str)).replace("s://", "sql://", 1)
