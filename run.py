import uvicorn

from app.config import PORT, HOST

if __name__ == "__main__":
    uvicorn.run("app.main:app", port=PORT, host=HOST, reload=True)
