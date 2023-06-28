from telebot.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

from database.db_manager import DBManager
from models.all_models import Product
from settings import config_bot


class Keyboard:
    def __init__(self):
        self.db = DBManager()
        self.markup = None

    def set_button(self, name: str, value: int | tuple[int, int] = None) -> KeyboardButton:
        """Создание Reply кнопки с текстом"""

        if config_bot.KEYBOARDS.get(name) is not None:

            # для кнопок предыдущий/следующий товар в заказе
            if isinstance(value, tuple):
                text_btn = f'{value[0]} из {value[1]}'
                return KeyboardButton(text_btn)

            # для отображения количества товара в заказе
            elif isinstance(value, int):
                return KeyboardButton(str(value))

            return KeyboardButton(config_bot.KEYBOARDS[name])

        # вывод reply кнопок для меню категорий
        elif config_bot.CATEGORIES_LIST.get(name):
            return KeyboardButton(config_bot.CATEGORIES_LIST[name])

        # если такая кнопка для админ-панели есть, то выводим ее, иначе выводим просто текст
        return KeyboardButton(config_bot.ADMIN_KEYBOARDS[name]) if config_bot.ADMIN_KEYBOARDS.get(name) else KeyboardButton(name)

    def set_inline_button(self, product: Product) -> InlineKeyboardButton:
        """Создание Inline кнопки для отображения товаров"""

        btn_text = f'{product.name} - {product.price}руб.'
        return InlineKeyboardButton(text=btn_text, callback_data=str(product.id))

    def start_menu(self) -> ReplyKeyboardMarkup:
        """Стартовое меню магазина"""

        self.markup = ReplyKeyboardMarkup(True)
        choose_goods_btn = self.set_button('CHOOSE_GOODS')
        about_btn = self.set_button('ABOUT')
        settings_btn = self.set_button('SETTINGS')
        self.markup.row(choose_goods_btn)
        self.markup.row(settings_btn, about_btn)

        return self.markup

    def back_btn(self) -> ReplyKeyboardMarkup:
        """Кнопка 'назад' """

        self.markup = ReplyKeyboardMarkup(True)
        back_button = self.set_button('<<')
        self.markup.row(back_button)

        return self.markup

    def categories_btn(self) -> ReplyKeyboardMarkup:
        """Reply кнопки для отображения категорий"""

        self.markup = ReplyKeyboardMarkup(True)

        for category in self.db.get_all_categories_with_product():
            self.markup.add(self.set_button(category.name.upper()))
        self.markup.add(self.set_button('<<'), self.set_button('ORDER'))

        return self.markup

    def get_product_button(self, category_name: str) -> InlineKeyboardMarkup:
        """Формирование inline-кнопок для отображения товаров"""

        self.markup = InlineKeyboardMarkup(row_width=1)

        for product in self.db.get_products_by_category(category_name):
            self.markup.add(self.set_inline_button(product))

        return self.markup

    def get_control_order_btn(self, count: int, total_count_products: int, current_position: int):
        """Кнопки управления заказом"""

        print(type((current_position, total_count_products)))
        self.markup = ReplyKeyboardMarkup(True)
        self.markup.add(self.set_button('X'))
        self.markup.add(self.set_button('DOWN'), self.set_button('AMOUNT_PRODUCT', value=count), self.set_button('UP'))
        self.markup.add(self.set_button('PREVIOUS'), self.set_button('AMOUNT_ORDERS',
                                                                     value=(current_position, total_count_products)),
                        self.set_button('NEXT'))
        self.markup.add(self.set_button('<<'), self.set_button('APPLY'))

        return self.markup

    def get_admin_btn(self) -> ReplyKeyboardMarkup:
        """Кнопки для админ панели"""

        self.markup = ReplyKeyboardMarkup(True)
        self.markup.add(self.set_button('ORDERS_LIST'), self.set_button('SEARCH_ORDER'))
        self.markup.add(self.set_button('PRODUCTS_LIST'), self.set_button('CATEGORIES_LIST'))
        self.markup.add(self.set_button('CREATE_PRODUCT'), self.set_button('CREATE_CATEGORY'))

        return self.markup

    def get_product_control_btn(self) -> ReplyKeyboardMarkup:
        """Кнопки для добавления продукта на складе и удаления продукта"""

        self.markup = ReplyKeyboardMarkup(True)
        self.markup.add(self.set_button('ADD_PRODUCT'))
        self.markup.add(self.set_button('DELETE_PRODUCT'))
        self.markup.add(self.set_button('BACK'))

        return self.markup
