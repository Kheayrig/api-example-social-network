from fastapi import FastAPI, HTTPException, status, Request
import logging

from app.db.base import DB
from app.api.handlers.auth import router as auth_router
from app.api.handlers.profile import router as profile_router
from app.api.handlers.feed import router as feed_router
from app.api.handlers.users import router as user_router
from app.utils.log_settings import JSONFormatter

app = FastAPI(title='Api-example (social network)')

app.include_router(user_router, prefix="/v1")
app.include_router(auth_router, prefix="/v1")
app.include_router(feed_router, prefix="/v1")
app.include_router(profile_router, prefix="/v1")

log = logging.getLogger()
log.setLevel("INFO")
std_handler = logging.StreamHandler()
std_handler.setFormatter(JSONFormatter())
file_handler = logging.FileHandler(filename="aesn.log", mode="a")
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(JSONFormatter())
log.addHandler(std_handler)
log.addHandler(file_handler)


@app.middleware('http')
async def handle_errors(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as e:
        log.warning(e, exc_info=True)
        raise e
    except ConnectionError as e:
        log.critical(e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Something is wrong, but we are fixing it...'
        )
    except Exception as e:
        log.error(e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Something is wrong, try again later...'
        )


@app.on_event("startup")
async def startup_event():
    await DB.connect_db()


@app.on_event("shutdown")
async def shutdown_event():
    await DB.disconnect_db()


