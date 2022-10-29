from fastapi import FastAPI, HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.db.base import DB
from app.api.handlers.auth import router as auth_router
from app.api.handlers.profile import router as profile_router
from app.api.handlers.feed import router as feed_router
from app.api.handlers.users import router as user_router
from app.utils.log_settings import log

app = FastAPI(title='Api-example (social network)')

app.include_router(user_router, prefix="/v1")
app.include_router(auth_router, prefix="/v1")
app.include_router(feed_router, prefix="/v1")
app.include_router(profile_router, prefix="/v1")


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    log.warning(exc, exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({
              "payload": None,
              "message": exc.detail,
              "title": None,
              "code": exc.status_code
            })
    )


@app.exception_handler(ConnectionError)
async def custom_connection_error_handler(request: Request, exc: ConnectionError):
    log.critical(exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content=jsonable_encoder({
              "payload": None,
              "message": "Something is wrong, but we are fixing it...",
              "title": None,
              "code": status.HTTP_504_GATEWAY_TIMEOUT
            })
    )


@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    log.critical(exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({
              "payload": None,
              "message": "Something is wrong, try again later...",
              "title": None,
              "code": status.HTTP_500_INTERNAL_SERVER_ERROR
            })
    )


@app.on_event("startup")
async def startup_event():
    await DB.connect_db()


@app.on_event("shutdown")
async def shutdown_event():
    await DB.disconnect_db()


