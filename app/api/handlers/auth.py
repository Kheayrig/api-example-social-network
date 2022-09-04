from fastapi import APIRouter, Body, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.schema import Profile, APIResponse
from app.api.security import create_access_token, verify_password, get_password_hash

from app.db.base import DB
from app.db.repositories.users_repository import UserRepository

router = APIRouter()


@router.post('/login', tags=["auth"], response_model=APIResponse)
async def authorize_user(request: OAuth2PasswordRequestForm = Depends()):
    """
    Authorization
    """
    if UserRepository.con is None:
        await DB.connect_db()
    user = await UserRepository.get_user_by_login(request.username)
    if user is False:
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
    message = {"access_token": access_token, "token_type": "bearer"}
    return {'status_code': status.HTTP_200_OK, 'content': str(message)}


@router.post("/registration", tags=["auth"], response_model=APIResponse)
async def registrate_new_user(user_form: Profile = Body(..., embed=True)):
    """
    Registration
    """
    if UserRepository.con is None:
        await DB.connect_db()
    user = await UserRepository.get_user_by_login(user_form.login)
    if user is False:
        res = await UserRepository.create_user(user_form.login, get_password_hash(user_form.password),
                                               user_form.first_name, user_form.last_name)
        if res:
            access_token = create_access_token(data={"sub": user_form.login})
            message = {"access_token": access_token['token'], "token_type": "bearer"}
            return {'status_code': status.HTTP_200_OK, 'content': str(message)}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Login not unique",
        headers={"WWW-Authenticate": "Bearer"},
    )
