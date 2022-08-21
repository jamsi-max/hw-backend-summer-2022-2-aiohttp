import typing

from aiohttp_session import setup, new_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet

from app.store.database.database import Database


if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.admin.accessor import AdminAccessor
        from app.store.bot.manager import BotManager
        from app.store.vk_api.accessor import VkApiAccessor
        from app.store.quiz.accessor import QuizAccessor

        self.quizzes = QuizAccessor(app)
        self.admins = AdminAccessor(app)
        self.vk_api = VkApiAccessor(app)
        self.bots_manager = BotManager(app)


def setup_store(app: "Application"):
    app.database = Database()
    app.store = Store(app)


def setup_session(app: "Application"):
    fernet_key = fernet.Fernet.generate_key()
    fernet_key_decode = fernet_key.decode('utf-8')
    setup(app, EncryptedCookieStorage(fernet_key_decode)) 
