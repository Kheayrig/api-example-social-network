import json

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse, StreamingResponse

from app.db.base import DB
from app.api.handlers.auth import router as auth_router
from app.api.handlers.profile import router as profile_router
from app.api.handlers.feed import router as feed_router
from app.api.handlers.users import router as user_router
from app.utils.log_settings import log

app = FastAPI(title='Api-example (social network)')
app.router.prefix = '/v1'
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(feed_router)
app.include_router(profile_router)


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


@app.middleware('http')
async def format_response(request: Request, call_next):
    if request.headers['accept'] != 'application/json':
        return await call_next(request)
    response: StreamingResponse = await call_next(request)
    status_code = response.status_code
    if status_code < 300:
        content = None
        if 'content-type' in response.headers and response.headers['content-type'] == 'application/json':
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            content = json.loads(response_body.decode('utf-8'))
        return JSONResponse(
            content=jsonable_encoder({
                "payload": content,
                "message": "OK",
                "title": None,
                "code": status_code
            }),
            status_code=status_code
        )
    else:
        return response


@app.on_event("startup")
async def startup_event():
    await DB.connect_db()


@app.on_event("shutdown")
async def shutdown_event():
    await DB.disconnect_db()


