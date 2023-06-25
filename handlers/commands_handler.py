import datetime

from loguru import logger

from handlers.handler import Handler


class CommandsHandler(Handler):

    def __init__(self, bot):
        super().__init__(bot)

    def pressed_start(self, message):
        """Отлавливаем команду старт"""

        logger.debug(f'Пользователь {message.from_user.id} запустил бота в {datetime.datetime.now()}')
        self.bot.send_message(message.from_user.id,
                              'Hiiiiii',
                              reply_markup=self.keyboard.start_menu())

    def handle(self):

        @self.bot.message_handler(commands=['start'])
        def start(message):
            if message.text == '/start':
                self.pressed_start(message)
