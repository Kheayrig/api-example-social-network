import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import DATA_PATH
from app.db.base import DB
from app.api.handlers.auth import router as auth_router
from app.api.handlers.profile import router as profile_router
from app.api.handlers.feed import router as feed_router
from app.api.handlers.users import router as user_router

app = FastAPI(title='Api-example (social network)')

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router, prefix="/v1")
app.include_router(auth_router, prefix="/v1")
app.include_router(feed_router, prefix="/v1")
app.include_router(profile_router, prefix="/v1")


@app.get('/', include_in_schema=False)
def hello_world():
    return{'hello': 'user'}


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    file_name = "favicon.ico"
    path = os.path.join(file_name)
    return FileResponse(DATA_PATH)


@app.on_event("startup")
async def startup_event():
    await DB.connect_db()


@app.on_event("shutdown")
async def shutdown_event():
    await DB.disconnect_db()


