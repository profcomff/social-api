from fastapi import Request
from fastapi.responses import JSONResponse

from social.exceptions import GroupNotFound, GroupRequestNotFound

from .base import app


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


@app.exception_handler(GroupNotFound)
def group_not_found(request: Request, exc: GroupNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            'details': 'Group not found',
            'ru': 'Группа не найдена',
            'group_id': exc.group_id,
        },
    )
