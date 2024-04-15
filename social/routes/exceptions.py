from fastapi import Request
from fastapi.responses import JSONResponse
from .base import app
from social.exceptions import GroupRequestNotFound


@app.exception_handler(GroupRequestNotFound)
def group_request_not_found(request: Request, exc: GroupRequestNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            'details': 'Group request not found',
            'ru': 'Запрос на создание группы не найден',
            'user_id': exc.user_id,
            'secret_key': exc.secret_key,
        },
    )
