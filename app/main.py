import uvicorn
from fastapi import FastAPI

from db.base import DB, db, Base, engine, UserData
from config import HOST, PORT
from api.handlers import users, auth, feed, profile


app = FastAPI(title='Api-example (social network)')

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(feed.router)
app.include_router(profile.router)


@app.on_event("startup")
async def startup_event():
    #await db.connect()
    await DB.connect_db()


@app.on_event("shutdown")
async def shutdown_event():
    #await db.disconnect()
    await DB.disconnect_db()


if __name__ == "__main__":
    #Base.metadata.create_all(bind=engine)
    uvicorn.run("main:app", port=PORT, host=HOST, reload=True)
