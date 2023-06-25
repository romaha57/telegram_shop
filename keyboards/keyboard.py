from telebot.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

from database.db_manager import DBManager
from settings import config_bot


class Keyboard:
    def __init__(self):
        self.db = DBManager()
        self.markup = None

    def set_button(self, name, value=None):
        """Создание Reply кнопки с текстом"""

        if config_bot.KEYBOARDS.get(name) is not None:

            # для кнопок предыдущий/следующий товар в заказе
            if isinstance(value, tuple):
                text_btn = f'{value[0]} из {value[1]}'
                return KeyboardButton(text_btn)

            # для отображения количества товара в заказе
            elif isinstance(value, int):
                return KeyboardButton(value)

            return KeyboardButton(config_bot.KEYBOARDS[name])

        return KeyboardButton(name)

    def set_inline_button(self, product):
        """Создание Inline кнопки для отображения товаров"""

        btn_text = f'{product.name} - {product.price}руб.'
        return InlineKeyboardButton(text=btn_text, callback_data=str(product.id))

    def start_menu(self):
        """Стартовое меню магазина"""

        self.markup = ReplyKeyboardMarkup(True)
        choose_goods_btn = self.set_button('CHOOSE_GOODS')
        about_btn = self.set_button('ABOUT')
        settings_btn = self.set_button('SETTINGS')
        self.markup.row(choose_goods_btn)
        self.markup.row(settings_btn, about_btn)

        return self.markup

    def back_btn(self):
        """Кнопка 'назад' """

        self.markup = ReplyKeyboardMarkup(True)
        back_button = self.set_button('<<')
        self.markup.row(back_button)

        return self.markup

    def categories_btn(self):
        """Reply кнопки для отображения категорий"""

        self.markup = ReplyKeyboardMarkup(True)

        for category in self.db.get_all_categories():
            self.markup.add(self.set_button(category.name.upper()))
        self.markup.add(self.set_button('<<'), self.set_button('ORDER'))

        return self.markup

    def get_product_button(self, category_name):
        """Формирование inline-кнопок для отображения товаров"""

        self.markup = InlineKeyboardMarkup(row_width=1)

        for product in self.db.get_products_by_category(category_name):
            self.markup.add(self.set_inline_button(product))

        return self.markup

    def get_control_order_btn(self, count, total_count_products, current_position):
        """Кнопки управления заказом"""

        self.markup = ReplyKeyboardMarkup(True)
        self.markup.add(self.set_button('X'))
        self.markup.add(self.set_button('DOWN'), self.set_button('AMOUNT_PRODUCT', value=count), self.set_button('UP'))
        self.markup.add(self.set_button('PREVIOUS'), self.set_button('AMOUNT_ORDERS', value=(current_position, total_count_products)), self.set_button('NEXT'))
        self.markup.add(self.set_button('<<'), self.set_button('APPLY'))

        return self.markup
