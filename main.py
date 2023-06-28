from loguru import logger
from telebot import StateMemoryStorage, TeleBot
from telebot.custom_filters import StateFilter

from handlers.main_handler import MainHandler
from settings import config_bot
from settings.logging import Logger


class Bot:
    def __init__(self):
        """Инициализация настроек для работы бота"""

        self.token = config_bot.BOT_TOKEN
        self.storage = StateMemoryStorage()
        self.bot = TeleBot(self.token, state_storage=self.storage)
        self.handler = MainHandler(self.bot)
        self.logger = Logger()

    def start(self):
        """Старт отлова всех handlers"""

        self.bot.add_custom_filter(StateFilter(self.bot))
        self.handler.handle()

    def run(self):
        """Запуск логирования и бота"""

        self.logger.run_logging()
        self.start()
        self.bot.polling(none_stop=True, skip_pending=True)


if __name__ == '__main__':
    try:
        bot = Bot()
        logger.debug('Бот запущен')
        bot.run()
    except Exception as error:
        logger.warning(f'Ошибка - {error}')
