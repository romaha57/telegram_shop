import abc

from telebot import TeleBot

from database.db_manager import DBManager
from keyboards.keyboard import Keyboard


class Handler(metaclass=abc.ABCMeta):
    """Абстрактный класс хендлера"""

    def __init__(self, bot: TeleBot):
        self.bot = bot
        self.db = DBManager()
        self.keyboard = Keyboard()

    @abc.abstractmethod
    def handle(self):
        pass
