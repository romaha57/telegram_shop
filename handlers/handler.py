import abc

from database.db_manager import DBManager
from keyboards.keyboard import Keyboard


class Handler(metaclass=abc.ABCMeta):

    def __init__(self, bot):
        self.bot = bot
        self.db = DBManager()
        self.keyboard = Keyboard()

    @abc.abstractmethod
    def handle(self):
        pass
