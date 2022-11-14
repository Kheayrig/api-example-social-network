from datetime import datetime, timedelta

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

from app.db.repositories.feed_repository import FeedRepository
from app.db.repositories.users_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str):
    res = pwd_context.verify(plain_password, hashed_password)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid password'
        )


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
        return login
    except JWTError:
        raise credentials_exception


def get_current_user(data: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has been expired or revoked",
        headers={"Authorization": "Bearer"},
    )
    return verify_token(data, credentials_exception)


def auth_check(access_token: str):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You're not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    login = get_current_user(access_token)
    return login


async def get_user_by_token(access_token: HTTPAuthorizationCredentials = Security(security)):
    login = auth_check(access_token.credentials)
    user = await UserRepository.get_user(login, UserRepository.login)
    return user


async def is_user_post(user_id: int, post_id: int):
    author_id = await FeedRepository.get_post(post_id)
    if author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have no access to update this post"
        )
