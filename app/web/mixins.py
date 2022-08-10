from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp.web_response import StreamResponse

from app.web.app import View


class AuthRequiredMixin(View):
    async def _iter(self) -> StreamResponse:
        if not self.request.admin:
            raise HTTPUnauthorized

        return await super()._iter()

