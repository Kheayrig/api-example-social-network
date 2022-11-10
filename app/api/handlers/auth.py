from fastapi import APIRouter, Body, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from app.api.schema import APIResponse, RegistrationForm
from app.api.security import create_access_token, verify_password, get_password_hash

from app.db.repositories.users_repository import UserRepository

router = APIRouter()


@router.post('/auth', tags=["auth"])
async def authorize_user(request: OAuth2PasswordRequestForm = Depends()):
    """
    Authorization
    """
    user = await UserRepository.get_user_by_login(request.username,
                                                  UserRepository.fields(UserRepository.login, UserRepository.hash))
    verify_password(request.password, user['hash'])
    # Generate a JWT Token
    access_token = create_access_token(data={"sub": user['login']})
    message = {"access_token": access_token, "token_type": "bearer"}
    return message


@router.post("/registration", tags=["auth"])
async def registrate_new_user(user_form: RegistrationForm = Body(..., embed=True)):
    """
    Registration
    """
    await UserRepository.create_user(user_form.login, get_password_hash(user_form.password),
                                     user_form.first_name, user_form.last_name)
    access_token = create_access_token(data={"sub": user_form.login})
    message = {"access_token": access_token, "token_type": "bearer"}
    return message
