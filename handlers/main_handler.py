from handlers.all_text_handler import AllTextHandler
from handlers.callback_handler import CallBackHandler
from handlers.commands_handler import CommandsHandler


class MainHandler:

    def __init__(self, bot):
        """Создание всех хендлеров"""

        self.bot = bot
        self.command_handler = CommandsHandler(self.bot)
        self.all_text_handler = AllTextHandler(self.bot)
        self.callback_handler = CallBackHandler(self.bot)

    def handle(self):
        """Регистрация хендлеров на отлавливание сообщений"""

        self.command_handler.handle()
        self.all_text_handler.handle()
        self.callback_handler.handle()
