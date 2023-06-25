import datetime

from loguru import logger
from telebot import TeleBot

from handlers.main_handler import MainHandler
from settings import config_bot
from settings.logging import Logger


class Bot:

    def __init__(self):
        self.token = config_bot.BOT_TOKEN
        self.bot = TeleBot(self.token)
        self.handler = MainHandler(self.bot)
        self.logger = Logger()

    def start(self):
        self.handler.handle()

    def run(self):
        self.logger.run_logging()
        self.start()
        self.bot.polling(none_stop=True, skip_pending=True)


if __name__ == '__main__':
    try:
        bot = Bot()
        logger.debug(f'Бот запущен в {datetime.datetime.now()}')
        bot.run()
    except Exception as error:
        logger.warning(f'Ошибка - {error}')
