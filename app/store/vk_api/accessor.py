import typing
from random import randint
from typing import Optional

from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateObject, \
    UpdateMessage

if typing.TYPE_CHECKING:
    from app.web.app import Application
    from app.store.vk_api.poller import Poller

BASE_API_URL = 'https://api.vk.com/method/'


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        from app.store.vk_api.poller import Poller

        self.session = ClientSession()
        await self._get_long_poll_service()
        self.poller = Poller(self.app.store)
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.session and not self.session.closed:
            await self.session.close()

        if self.poller and self.poller.is_running:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        url = self._build_query(
            host=BASE_API_URL,
            method='groups.getLongPollServer',
            params={
                'access_token': self.app.config.bot.token,
                'group_id': self.app.config.bot.group_id
            }
        )
        self.logger.info(f'url {url}')
        async with self.session.get(url) as resp:
            data = await resp.json()
            data = data["response"]
            self.logger.info(f'data {data}')
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]

    async def poll(self):
        url = self._build_query(
            host=self.server,
            method='',
            params={
                'act': 'a_check',
                'key': self.key,
                'ts': self.ts,
                'wait': 25
            }
        )
        async with self.session.get(url) as resp:
            data = await resp.json()
            self.logger.info(f'poll data {data}')
            self.ts = data["ts"]
            updates = []
            for event in data.get('updates', []):
                if event["type"] == 'message_new':
                    updates.append(Update(
                        type=event["type"],
                        object=UpdateObject(
                            message=UpdateMessage(
                                from_id=event["object"]["message"]["from_id"],
                                text=event["object"]["message"]["text"],
                                id=event["object"]["message"]["id"],
                            )
                        )
                    ))
        return updates

    async def send_message(self, message: Message) -> None:
        url = self._build_query(
            host=BASE_API_URL,
            method='messages.send',
            params={
                'user_id': message.user_id,
                'message': message.text,
                'access_token': self.app.config.bot.token,
                'random_id': randint(0, 10000000)
            }
        )
        async with self.session.get(url) as resp:
            data = await resp.json()
            self.logger.info(f'send message data {data}')
