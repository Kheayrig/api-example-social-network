from fastapi import APIRouter, Body, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.schema import Profile
from app.api.security import create_access_token, verify_password, get_password_hash

from app.db.base import DB
from app.db.repositories.users_repository import UserRepository

router = APIRouter()


@router.post('/login', tags=["auth"])
async def login(request: OAuth2PasswordRequestForm = Depends()):
    if UserRepository.con is None:
        await DB.connect_db()
    user = await UserRepository.get_user_by_login(request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Invalid Credentials'
        )
    if not verify_password(request.password, user['hash']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid Password'
        )
    # Generate a JWT Token
    access_token = create_access_token(data={"sub": user['login']})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/registration", tags=["auth"])
async def registration(user_form: Profile = Body(..., embed=True)):
    if UserRepository.con is None:
        await DB.connect_db()
    user = await UserRepository.get_user_by_login(user_form.login)
    if user is False:
        res = await UserRepository.create_user(user_form.login, get_password_hash(user_form.password),
                                               user_form.first_name, user_form.last_name)
        if res:
            access_token = create_access_token(data={"sub": user_form.login})
            return {"access_token": access_token['token'], "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Login not unique",
        headers={"WWW-Authenticate": "Bearer"},
    )
