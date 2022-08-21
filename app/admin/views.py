from hashlib import sha256
from urllib import request

from aiohttp_apispec import (docs,
                             request_schema,
                             response_schema)
from aiohttp_session import new_session, get_session
from aiohttp.web_exceptions import (HTTPNotFound,
                                    HTTPUnauthorized,
                                    HTTPForbidden)

from app.admin.schemes import AdminSchema, AdminSchemaResponse
from app.web.app import View
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response, login_required


class AdminLoginView(View):
    @docs(
        tags=['VKBot'],
        summary='Administrator Authorization',
        description='Return user information along with the active session'
    )
    @request_schema(AdminSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        data = self.request.get('data')
        admin = await (
            self.request.app.store.admins.get_by_email(
                email=data.get('email'),
            )
        )
        password = sha256(data.get('password').encode('utf-8')).hexdigest()

        if admin is None or admin.password != password:
            raise HTTPForbidden
        
        session = await new_session(self.request)
        session['manager'] = AdminSchemaResponse().dump(admin)
        
        return json_response(
            data=AdminSchemaResponse().dump(admin)
        )


class AdminCurrentView(View):
    @login_required()
    @docs(
        tags=['VKBot'],
        summary='Personal information',
        description='Gives information about the manager'
    )
    @response_schema(OkResponseSchema, 200)
    async def get(self):
        session = await get_session(self.request)
        manager = session['manager']
        
        admin = await self.request.app.store.admins.get_by_email(
                email=manager['email'],
        )
        
        return json_response(
            data=AdminSchemaResponse().dump(admin)
        )
