import functools
from typing import Any, Optional

from aiohttp_session import get_session
from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_exceptions import (HTTPNotFound,
                                    HTTPUnauthorized,
                                    HTTPForbidden)
from aiohttp.web_response import Response


def json_response(data: Any = None, status: str = "ok") -> Response:
    if data is None:
        data = {}
    return aiohttp_json_response(
        data={
            "status": status,
            "data": data,
        }
    )


def error_json_response(
    http_status: int,
    status: str = "error",
    message: Optional[str] = None,
    data: Optional[dict] = None,
):
    if data is None:
        data = {}
    return aiohttp_json_response(
        status=http_status,
        data={
            'status': status,
            'message': str(message),
            'data': data,
        }
    )


def login_required(**kwargs):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args):
            request = args[0].request
            session = await get_session(request)
            manager = session.get('manager', None)

            if manager is None:
                raise HTTPUnauthorized

            admin = await request.app.store.admins.get_by_email(
                email=manager.get('email'),
            )

            if admin is None or admin.id != manager.get('id'):
                raise HTTPForbidden

            return await func(*args)
        return wrapped
    return wrapper




