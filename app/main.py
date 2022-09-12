from fastapi import FastAPI, HTTPException, status, Request

from app.db.base import DB
from app.api.handlers.auth import router as auth_router
from app.api.handlers.profile import router as profile_router
from app.api.handlers.feed import router as feed_router
from app.api.handlers.users import router as user_router

app = FastAPI(title='Api-example (social network)')

app.include_router(user_router, prefix="/v1")
app.include_router(auth_router, prefix="/v1")
app.include_router(feed_router, prefix="/v1")
app.include_router(profile_router, prefix="/v1")


@app.middleware('http')
async def raise_server_exception(request: Request, call_next):
    try:
        if DB.con is None:
            await DB.connect_db()
        response = await call_next(request)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Something is wrong, try again later'
        )


@app.on_event("startup")
async def startup_event():
    await DB.connect_db()


@app.on_event("shutdown")
async def shutdown_event():
    await DB.disconnect_db()


