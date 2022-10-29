from fastapi import APIRouter, Body, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from app.api.schema import RegistrationForm, APIResponse
from app.api.security import create_access_token, verify_password, get_password_hash

from app.db.repositories.users_repository import UserRepository

router = APIRouter()


@router.post('/auth', tags=["auth"])
async def authorize_user(request: OAuth2PasswordRequestForm = Depends()):
    """
    Authorization
    """
    user = await UserRepository.get_user_by_login(request.username)
    verify_password(request.password, user['hash'])
    # Generate a JWT Token
    access_token = create_access_token(data={"sub": user['login']})
    message = {"access_token": access_token, "token_type": "bearer"}
    return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder({
                "payload": message,
                "message": "Authorization has been succeeded",
                "title": None,
                "code": status.HTTP_200_OK
            })
        )


@router.post("/registration", tags=["auth"], response_model=APIResponse)
async def registrate_new_user(user_form: RegistrationForm = Body(..., embed=True)):
    """
    Registration
    """
    try:
        await UserRepository.get_user_by_login(user_form.login)
    except HTTPException:
        await UserRepository.create_user(user_form.login, get_password_hash(user_form.password),
                                         user_form.first_name, user_form.last_name)
        access_token = create_access_token(data={"sub": user_form.login})
        message = {"access_token": access_token, "token_type": "bearer"}
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder({
                "payload": message,
                "message": "Registration has been succeeded",
                "title": None,
                "code": status.HTTP_201_CREATED
            })
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Login not unique",
        headers={"WWW-Authenticate": "Bearer"},
    )
