from aiohttp.web_exceptions import HTTPForbidden
from aiohttp_apispec import response_schema, request_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema, AdminResponseSchema, \
    AdminOkResponseSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminOkResponseSchema)
    async def post(self):
        email, password = self.data["email"], self.data["password"]
        admin = await self.store.admins.get_by_email(email)
        if not admin or not admin.check_password(password):
            raise HTTPForbidden

        session = await new_session(self.request)
        session["admin"] = AdminResponseSchema().dump(admin)
        return json_response(data=AdminResponseSchema().dump(admin))


class AdminCurrentView(AuthRequiredMixin, View):
    async def get(self):
        return json_response(
            data={"admin": AdminResponseSchema().dump(self.request.admin)}
        )
