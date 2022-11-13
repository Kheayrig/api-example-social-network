from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.schema import APIResponse, RegistrationForm, AccessToken
from app.api.security import create_access_token, verify_password, get_password_hash

from app.db.repositories.users_repository import UserRepository

router = APIRouter()


@router.post('/auth', tags=["auth"], response_model=AccessToken)
async def authorize_user(request: OAuth2PasswordRequestForm = Depends()):
    """
    Authorization
    """
    user = await UserRepository.get_user(request.username, UserRepository.login,
                                         UserRepository.fields(UserRepository.login, UserRepository.hash))
    verify_password(request.password, user['hash'])
    jwt = create_access_token(data={"sub": user['login']})
    return {"access_token": jwt, "token_type": "bearer"}


@router.post("/registration", tags=["auth"])
async def registrate_new_user(user_form: RegistrationForm = Body(..., embed=True)):
    """
    Registration
    """
    await UserRepository.create_user(user_form.login, get_password_hash(user_form.password),
                                     user_form.first_name, user_form.last_name)
    jwt = create_access_token(data={"sub": user_form.login})
    return {"access_token": jwt, "token_type": "bearer"}
