from loguru import logger
from telebot import TeleBot
from telebot.types import Message

from handlers.handler import Handler
from settings import config_bot
from settings.messages import MESSAGES
from states.admin_state import AdminSignInState


class CommandsHandler(Handler):

    def __init__(self, bot: TeleBot):
        super().__init__(bot)

    def pressed_start(self, message: Message) -> None:
        """Обрабатываем нажатие старт"""

        logger.debug(f'Пользователь {message.from_user.id} запустил бота')
        self.bot.send_message(message.from_user.id,
                              MESSAGES['START'],
                              parse_mode='html',
                              reply_markup=self.keyboard.start_menu())

    def pressed_admin(self, message: Message) -> None:
        """Обрабатываем нажатие /admin"""

        logger.debug(f'Пользователь {message.from_user.id} хочет зайти в админку')
        self.bot.send_message(message.from_user.id,
                              'Введите пароль для админки:')
        self.bot.set_state(message.from_user.id, AdminSignInState.password, message.chat.id)

    def handle(self):

        @self.bot.message_handler(commands=['start', 'admin'])
        def start(message: Message) -> None:
            if message.text == '/start':
                self.pressed_start(message)
            elif message.text == '/admin':
                self.pressed_admin(message)

        @self.bot.message_handler(state=AdminSignInState.password)
        def check_password(message: Message) -> None:
            if message.text == config_bot.ADMIN_PASSWORD:
                self.bot.send_message(message.from_user.id,
                                      'Вы вошли в админ-панель',
                                      reply_markup=self.keyboard.get_admin_btn())

                # уведомление о добавлении категории в настройки(settings.config_bot)
                if self.db.find_category_without_button():
                    self.bot.send_message(message.from_user.id,
                                          MESSAGES['NOTIFICATION'].format(
                                              self.db.find_category_without_button()
                                          ),
                                          parse_mode='html')

                self.bot.delete_state(message.from_user.id, message.chat.id)
            else:
                self.bot.send_message(message.from_user.id, 'Неверный пароль. Проверьте регистр')
