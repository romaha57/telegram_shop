from loguru import logger
from telebot import TeleBot
from telebot.types import CallbackQuery

from handlers.handler import Handler
from settings.messages import MESSAGES


class CallBackHandler(Handler):

    def __init__(self, bot: TeleBot):
        super().__init__(bot)

    def pressed_product_btn(self, callback: CallbackQuery) -> None:
        """Отлавливаем нажатие кнопки с товаром и создание заказа"""

        self.db.create_order(
            product_id=callback.data,
            user_id=callback.from_user.id
        )

        logger.debug(f'Пользователь {callback.from_user.id} добавил товар с ID = {callback.data} в заказ')

        self.bot.answer_callback_query(callback.id,
                                       MESSAGES['PRODUCT'].format(
                                           self.db.get_product_by_id(callback.data).name,
                                           self.db.get_product_by_id(callback.data).price,
                                           self.db.get_count_product_in_orders(callback.data, callback.from_user.id),
                                           self.db.get_product_by_id(callback.data).quantity),
                                       show_alert=True)

    def handle(self):

        @self.bot.callback_query_handler(func=lambda callback: True)
        def callback_handler(callback: CallbackQuery) -> None:
            product_id = callback.data
            if product_id.isdigit():
                self.pressed_product_btn(callback)
