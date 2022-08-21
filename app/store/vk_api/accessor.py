import random
import typing
from typing import List, Optional

from aiohttp import ClientSession, TCPConnector

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateObject, UpdateMessage
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

PATH_API = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        # TODO: добавить создание aiohttp ClientSession,
        #  получить данные о long poll сервере с помощью метода groups.getLongPollServer
        #  вызвать метод start у Poller
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)
        self.poller = Poller(store=app.store)
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        # TODO: закрыть сессию и завершить поллер
        if self.session:
            await self.session.close()
        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        async with self.session.get(
            self._build_query(
                host=PATH_API,
                method="groups.getLongPollServer",
                params={
                    "group_id": self.app.config.bot.group_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as response:
            data_json = response.json()
            data = data_json.get('response')
            self.key = data.get('key')
            self.server = data.get('server')
            self.ts = data.get('ts')

    async def poll(self):
        async with self.session.get(
            self._build_query(
                host=self.server,
                method='',
                params={
                    'act': 'a_check',
                    'key': self.key,
                    'ts': self.ts,
                    'wait': 60,
                },
            )
        ) as response:
            data = await response.json()
            self.ts = data.get('ts')
            updates = []
            raw_updates = data.get('updates', [])
            for update in raw_updates:
                updates.append(
                    Update(
                        type=update.get('type'),
                        object=UpdateObject(
                            message=UpdateMessage(
                                from_id=update['object']['message']['from_id'],
                                test=update['object']['message']['text'],
                                id=update['object']['message']['id'],
                            )
                        ),
                    )
                )
        return updates

    async def send_message(self, message: Message) -> None:
        async with self.session.get(
            self._build_query(
                PATH_API,
                'messages.send',
                params={
                    'random_id': random.randint(1, 2 ** 32),
                    'peer_id': message.user_id,
                    'message': message.text,
                    'access_token': self.app.config.bot.token,
                },
            )
        ) as response:
            data = await response.json()
            self.logger.info(data)
