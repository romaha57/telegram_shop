import datetime

from loguru import logger
from telebot import TeleBot
from telebot.types import Message

from handlers.handler import Handler
from models.all_models import Product
from settings import config_bot
from settings.messages import MESSAGES
from states.admin_state import (AddProductState, CreateCategoryState,
                                CreateProductState, DeleteProductState,
                                SearchState)


class AllTextHandler(Handler):

    def __init__(self, bot: TeleBot):
        super().__init__(bot)
        self.step = 0

    def pressed_about_btn(self, message: Message) -> None:
        """При нажатии кнопки 'О магазине' """

        self.bot.send_message(message.from_user.id,
                              MESSAGES['ABOUT'],
                              parse_mode='html',
                              reply_markup=self.keyboard.back_btn())

    def pressed_back_btn(self, message: Message) -> None:
        """При нажатии кнопки 'назад' """

        self.bot.send_message(message.from_user.id,
                              'Вы вернулись назад',
                              reply_markup=self.keyboard.start_menu())

    def pressed_settings_btn(self, message: Message) -> None:
        """При нажатии кнопки 'Настройки' """

        self.bot.send_message(message.from_user.id,
                              MESSAGES['SETTINGS'],
                              parse_mode='html',
                              reply_markup=self.keyboard.back_btn())

    def pressed_choose_good_btn(self, message: Message) -> None:
        """При нажатии кнопки 'Выбрать товар' """

        self.bot.send_message(message.from_user.id,
                              'Каталог товаров',
                              reply_markup=self.keyboard.categories_btn())

    def pressed_product_btn(self, message: Message) -> None:
        """При нажатии кнопки выбора категории """

        self.bot.send_message(message.from_user.id,
                              MESSAGES['CHOOSE_CATEGORY'].format(
                                 message.text
                              ),
                              parse_mode='html',
                              reply_markup=self.keyboard.get_product_button(message.text.split()[1]))

    def pressed_order_btn(self, message: Message) -> None:
        """При нажатии кнопки 'Заказ' """

        products_id_in_order = self.db.get_users_card(user_id=message.from_user.id)
        product = self.db.get_product_by_id(products_id_in_order[self.step])

        self.send_message_order_item(message=message, product=product)

    def send_message_order_item(self, message: Message, product: Product) -> None:
        """Отправляем сообщение с позицией товара в заказе и информацией по заказу"""

        self.bot.send_message(message.from_user.id,
                              MESSAGES['PRODUCT_POSITION'].format(self.step + 1),
                              parse_mode='html')

        self.bot.send_message(message.from_user.id,
                              MESSAGES['ORDER'].format(
                                  product.name,
                                  product.price,
                                  self.db.get_count_product_in_orders(product_id=product.id, user_id=message.from_user.id),
                                  product.quantity,
                                  self.db.get_total_product_price(product=product, user_id=message.from_user.id)
                                ),
                              parse_mode='html',
                              reply_markup=self.keyboard.get_control_order_btn(
                                  count=self.db.get_count_product_in_orders(product_id=product.id, user_id=message.from_user.id),
                                  total_count_products=self.db.get_count_products_in_order(user_id=message.from_user.id),
                                  current_position=self.step + 1
                              ))

    def pressed_up_down_btn(self, message: Message) -> None:
        """При нажатии кнопки 'Добавить/Убавить количество товара' """

        products_id_in_order = self.db.get_users_card(user_id=message.from_user.id)
        product = self.db.get_product_by_id(products_id_in_order[self.step])

        if message.text == config_bot.KEYBOARDS['UP']:

            # если товар есть на складе
            if product.quantity > 0:
                # уменьшаем количество на складе
                self.db.update_product_in_stock(product_id=product.id)
                # увеличиваем количество в заказе
                self.db.increase_quantity_product_in_order(product_id=product.id, user_id=message.from_user.id)
        elif message.text == config_bot.KEYBOARDS['DOWN']:

            # если количество товара в заказе больше 0
            if self.db.get_count_product_in_orders(product_id=product.id, user_id=message.from_user.id) > 0:
                # увеличиваем количество на складе
                self.db.add_product_in_stock(product_id=product.id)

                # уменьшаем количество в заказе
                self.db.decrease_quantity_product_in_order(product_id=product.id, user_id=message.from_user.id)

        self.send_message_order_item(message, product)

    def pressed_next_previous_btn(self, message: Message) -> None:
        """При нажатии кнопки 'Предыдущий/Следующий товар в заказе' """

        if message.text == config_bot.KEYBOARDS['NEXT'] and self.step < self.db.get_count_products_in_order(user_id=message.from_user.id) - 1:
            self.step += 1
        elif message.text == config_bot.KEYBOARDS['PREVIOUS'] and self.step != 0:
            self.step -= 1

        products_id_in_order = self.db.get_users_card(user_id=message.from_user.id)
        product = self.db.get_product_by_id(products_id_in_order[self.step])

        self.send_message_order_item(message, product)

    def pressed_delete_btn(self, message: Message) -> None:
        """При нажатии кнопки 'Удалить товар в заказе' """

        products_id_in_order = self.db.get_users_card(user_id=message.from_user.id)
        product = self.db.get_product_by_id(products_id_in_order[self.step])
        product_name = product.name

        if products_id_in_order:
            self.db.delete_product_in_order(product_id=product.id, user_id=message.from_user.id)

            self.bot.send_message(message.from_user.id,
                                  MESSAGES['DELETE_PRODUCT_IN_ORDER'].format(
                                      product_name
                                  ),
                                  parse_mode='html')
            logger.debug(
                f'Пользователь {message.from_user.id} удалил {product_name} из заказа')

    def pressed_apply_order_btn(self, message: Message) -> None:
        """При нажатии кнопки 'Оформить заказ' """

        self.bot.send_message(message.from_user.id,
                              MESSAGES['APPLY_ORDER'].format(
                                  self.db.get_total_cost_order_by_user(user_id=message.from_user.id)
                              ),
                              reply_markup=self.keyboard.categories_btn(),
                              parse_mode='html')

        logger.debug(f'Пользователь {message.from_user.id} оформил заказ')
        self.db.delete_order(user_id=message.from_user.id)
        logger.debug(f'У пользователя {message.from_user.id} очищена корзина')

    def pressed_orders_list_btn(self, message: Message) -> None:
        """При нажатии кнопки 'Список заказов' в админке """

        orders_list = self.db.get_all_orders()

        if orders_list:
            for order in orders_list:
                self.bot.send_message(message.from_user.id,
                                      MESSAGES['ORDER_INFO'].format(
                                          order.id,
                                          order.user_id,
                                          self.db.get_product_by_id(product_id=order.product_id).name,
                                          order.quantity,
                                          self.db.get_total_product_price(user_id=message.from_user.id, product=self.db.get_product_by_id(product_id=order.product_id)),
                                          order.created_at.strftime('%d-%m-%Y %H:%M')
                                      ),
                                      parse_mode='html',
                                      reply_markup=self.keyboard.get_admin_btn())

            logger.debug(f'Пользователь {message.from_user.id} запросил список заказов в админке в {datetime.datetime.now()}')
        else:
            self.bot.send_message(message.from_user.id,
                                  '<i>Заказов нет...</i>',
                                  parse_mode='html',
                                  reply_markup=self.keyboard.get_admin_btn())

    def pressed_search_order_btn(self, message: Message) -> None:
        """При нажатии кнопки 'Поиск заказа' в админке """

        self.bot.send_message(message.from_user.id,
                              'Введите id пользователя')
        self.bot.set_state(message.from_user.id, SearchState.user_id, message.chat.id)

    def search_order(self, message: Message) -> None:
        """Поиск заказа по user_id"""

        user_products_card = self.db.get_users_card(user_id=message.text)
        total_cost = self.db.get_total_cost_order_by_user(user_id=message.text)
        for product_id in user_products_card:
            product = self.db.get_product_by_id(product_id=product_id)

            self.bot.send_message(message.from_user.id,
                                  MESSAGES['SEARCH_RESULT'].format(
                                      product.name,
                                      self.db.order_by_user_and_product(user_id=message.text,
                                                                        product_id=product.id).quantity,
                                      product.price,
                                      self.db.get_total_product_price(user_id=message.text,
                                                                      product=product)
                                  ),
                                  parse_mode='html')
        logger.debug(
            f'Пользователь {message.from_user.id} искал заказы пользователя с id {message.text} в админке в {datetime.datetime.now()}')

        self.bot.send_message(message.from_user.id,
                              MESSAGES['TOTAL_PRICE_ORDERS_BY_USER'].format(
                                  message.text,
                                  total_cost
                              ),
                              parse_mode='html',
                              reply_markup=self.keyboard.get_admin_btn())

    def pressed_product_list_btn(self, message: Message) -> None:
        """При нажатии кнопки 'Список продуктов' в админке """

        all_products = self.db.get_all_products()

        for product in all_products:
            self.bot.send_message(message.from_user.id,
                                  MESSAGES['PRODUCT_INFO'].format(
                                      product.id,
                                      product.name,
                                      product.price,
                                      product.quantity,
                                      self.db.get_category_by_id(category_id=product.category_id)
                                  ),
                                  parse_mode='html',
                                  reply_markup=self.keyboard.get_product_control_btn())
        logger.debug(
            f'Пользователь {message.from_user.id} запросил список товаров в админке в {datetime.datetime.now()}')

    def pressed_categories_list_btn(self, message: Message) -> None:
        """При нажатии кнопки 'Список категорий' в админке """

        all_categories = self.db.get_all_categories()

        for category in all_categories:
            self.bot.send_message(message.from_user.id,
                                  MESSAGES['CATEGORY_INFO'].format(
                                      category.id,
                                      category.name
                                  ),
                                  parse_mode='html',
                                  reply_markup=self.keyboard.get_admin_btn())

        logger.debug(
            f'Пользователь {message.from_user.id} запросил список категорий в админке')

    def pressed_create_category_btn(self, message: Message) -> None:
        """При нажатии кнопки 'Создать категорию' в админке """

        self.bot.send_message(message.from_user.id,
                              'Введите название категории')

        self.bot.set_state(message.from_user.id, CreateCategoryState.name, message.chat.id)
        logger.debug(f'Пользователь в админке: {message.from_user.id} установил название категории для создания ')

    def pressed_create_product(self, message: Message) -> None:
        """При нажатии кнопки 'Создать продукт' в админке """

        self.bot.send_message(message.from_user.id,
                              'Введите название продукта')
        self.bot.set_state(message.from_user.id, CreateProductState.name, message.chat.id)
        logger.debug(f'Пользователь в админке: {message.from_user.id} установил название продукта для создания ')

    def pressed_add_product(self, message: Message) -> None:
        """При нажатии кнопки 'Добавить количество продукта' в админке """

        self.bot.send_message(message.from_user.id,
                              'Введите id товара')
        self.bot.set_state(message.from_user.id, AddProductState.id, message.chat.id)

    def pressed_delete_product(self, message: Message) -> None:
        """При нажатии кнопки 'Удалить продукт из БД' в админке """

        self.bot.send_message(message.from_user.id,
                              'Введите id товара')
        self.bot.set_state(message.from_user.id, DeleteProductState.id, message.chat.id)

    def pressed_back_admin_btn(self, message: Message) -> None:
        """При нажатии кнопки 'назад' в админке """

        self.bot.send_message(message.from_user.id,
                              'Вы вернулись назад',
                              reply_markup=self.keyboard.get_admin_btn())

    def handle(self):

        @self.bot.message_handler(state=SearchState.user_id)
        def search_order_func(message: Message) -> None:
            """Отлавливаем состояние при поиске заказа по user_id"""

            if message.text.isdigit() and len(str(message.text)) == 9:
                self.search_order(message)
                logger.debug('Удаляем состояния по поиску заказа')
                self.bot.delete_state(message.from_user.id, message.chat.id)
            else:
                self.bot.send_message(message.from_user.id,
                                      'id должен состоять только из цифр/'
                                      'количество цифр должно быть равно 9')

        @self.bot.message_handler(state=CreateCategoryState.name)
        def create_category(message: Message) -> None:
            """Отлавливаем состояние при создании категории(name)"""

            if message.text.isalpha():
                self.db.create_category(name=message.text)
                self.bot.delete_state(message.from_user.id, message.chat.id)
                self.bot.send_message(message.from_user.id,
                                      MESSAGES['CREATE_CATEGORY'].format(
                                          message.text
                                      ),
                                      parse_mode='html',
                                      reply_markup=self.keyboard.get_admin_btn())
                logger.debug(
                    f'Пользователь в админке: {message.from_user.id} создал категорию - {message.text} ')

            else:
                self.bot.send_message(message.from_user.id,
                                      'Имя должно состоять из букв')

        @self.bot.message_handler(state=CreateProductState.name)
        def create_product_name(message: Message) -> None:
            """Отлавливаем состояние при создании товара(name)"""

            with self.bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data["product_name"] = message.text

            logger.debug(f'Пользователь в админке: {message.from_user.id} установил название продукта для создания ')

            self.bot.send_message(message.from_user.id,
                                  'Введите цену товара в рублях')
            self.bot.set_state(message.from_user.id, CreateProductState.price, message.chat.id)

        @self.bot.message_handler(state=CreateProductState.price)
        def create_product_price(message: Message) -> None:
            """Отлавливаем состояние при создании товара(price)"""

            if message.text.isdigit():
                with self.bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data["product_price"] = message.text

                logger.debug(
                    f'Пользователь в админке: {message.from_user.id} установил цену продукта для создания ')

                self.bot.send_message(message.from_user.id,
                                      'Введите количество товара на складе')
                self.bot.set_state(message.from_user.id, CreateProductState.quantity, message.chat.id)

            else:
                self.bot.send_message(message.from_user.id,
                                      'Цена должна быть числом')

        @self.bot.message_handler(state=CreateProductState.quantity)
        def create_product_quantity(message: Message) -> None:
            """Отлавливаем состояние при создании товара(quantity)"""

            if message.text.isdigit():
                with self.bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data["product_quantity"] = message.text

                logger.debug(
                    f'Пользователь в админке: {message.from_user.id} '
                    f'установил количество продукта на складе для создания ')

                self.bot.send_message(message.from_user.id,
                                      'Введите id категории для данного товара')

                self.bot.set_state(message.from_user.id, CreateProductState.category_id, message.chat.id)

            else:
                self.bot.send_message(message.from_user.id,
                                      'Количество товара должно быть число')

        @self.bot.message_handler(state=CreateProductState.category_id)
        def create_product_category_id(message: Message) -> None:
            """Отлавливаем состояние при создании товара(category_id)"""

            if message.text.isdigit():
                with self.bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data["product_category_id"] = message.text

                logger.debug(
                    f'Пользователь в админке: {message.from_user.id} установил id категории при создании продукта')

                product = self.db.create_product(data)
                self.bot.send_message(message.from_user.id,
                                      'Товар успешно создан')
                self.bot.send_message(message.from_user.id,
                                      MESSAGES['PRODUCT_INFO'].format(
                                          product.id,
                                          product.name,
                                          product.price,
                                          product.quantity,
                                          self.db.get_category_by_id(product.category_id)
                                      ),
                                      parse_mode='html',
                                      reply_markup=self.keyboard.get_admin_btn())
                logger.debug(
                    f'Пользователь в админке: {message.from_user.id} добавил продукт(id={product.id}/{product.name}) в БД ')
                self.bot.delete_state(message.from_user.id, message.chat.id)

            else:
                self.bot.send_message(message.from_user.id,
                                      'ID категории должно быть число \n'
                                      '(Просмотреть id всех категории можно по кнопке ниже)',
                                      reply_markup=self.keyboard.get_admin_btn())

        @self.bot.message_handler(state=AddProductState.id)
        def add_product_id(message: Message) -> None:
            """Отлавливаем состояние при добавлении продукта на склад(id)"""

            if message.text.isdigit() and self.db.has_product(product_id=message.text):

                with self.bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data["product_id"] = int(message.text)

                self.bot.send_message(message.from_user.id,
                                      'Введите количество добавляемого товара:')
                self.bot.set_state(message.from_user.id, AddProductState.quantity, message.chat.id)
            else:
                self.bot.send_message(message.from_user.id,
                                      'id должен состоять только из цифр/'
                                      'или такого id нет в базе данных')

        @self.bot.message_handler(state=AddProductState.quantity)
        def add_product_quantity(message: Message) -> None:
            """Отлавливаем состояние при добавлении продукта на склад(количество)"""

            if message.text.isdigit():
                with self.bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data["product_quantity"] = message.text

                self.db.add_product_quantity(data)
                product = self.db.get_product_by_id(product_id=data['product_id'])
                self.bot.send_message(message.from_user.id,
                                      MESSAGES['ADD_PRODUCT'].format(
                                          product.name,
                                          data['product_quantity'],
                                          product.quantity
                                      ),
                                      parse_mode='html',
                                      reply_markup=self.keyboard.get_admin_btn())

                self.bot.delete_state(message.from_user.id, message.chat.id)
            else:
                self.bot.send_message(message.from_user.id,
                                      'Количество товара должно быть цифрой')

        @self.bot.message_handler(state=DeleteProductState.id)
        def delete_product_id(message: Message) -> None:
            """Отлавливаем состояние при удалении продукта (id)"""

            if message.text.isdigit() and self.db.has_product(product_id=message.text):
                product_id = int(message.text)
                product_name = self.db.get_product_by_id(product_id=product_id).name

                self.db.delete_product(product_id=int(message.text))
                self.bot.send_message(message.from_user.id,
                                      MESSAGES['DELETE_PRODUCT'].format(
                                          product_name
                                      ),
                                      parse_mode='html',
                                      reply_markup=self.keyboard.get_admin_btn())

                self.bot.delete_state(message.from_user.id, message.chat.id)
            else:
                self.bot.send_message(message.from_user.id,
                                      'id должен состоять только из цифр/'
                                      'или такого id нет в базе данных')

        @self.bot.message_handler(func=lambda message: True)
        def all_text(message: Message) -> None:
            if message.text == config_bot.KEYBOARDS['ABOUT']:
                logger.debug(f'Пользователь: {message.from_user.id} нажал "about"')
                self.pressed_about_btn(message)

            elif message.text == config_bot.KEYBOARDS['<<']:
                logger.debug(f'Пользователь: {message.from_user.id} нажал "назад"')
                self.pressed_back_btn(message)

            elif message.text == config_bot.KEYBOARDS['SETTINGS']:
                logger.debug(f'Пользователь: {message.from_user.id} нажал "настройки"')
                self.pressed_settings_btn(message)

            elif message.text == config_bot.KEYBOARDS['CHOOSE_GOODS']:
                logger.debug(f'Пользователь: {message.from_user.id} нажал "каталог товаров"')
                self.pressed_choose_good_btn(message)

            elif message.text in (config_bot.CATEGORIES_LIST['IPHONE'], config_bot.CATEGORIES_LIST['MACBOOK'], config_bot.CATEGORIES_LIST['APPLEWATCH']):
                logger.debug(f'Пользователь: {message.from_user.id} нажал на саму категорию')
                self.pressed_product_btn(message)

            elif message.text == config_bot.KEYBOARDS['ORDER']:
                logger.debug(f'Пользователь: {message.from_user.id} нажал "заказ"')
                if self.db.has_order(user_id=message.from_user.id):
                    self.pressed_order_btn(message)
                else:
                    # если нет заказов у данного пользователя
                    logger.debug(f'У пользователя: {message.from_user.id} пустой список заказов')
                    self.bot.send_message(message.from_user.id,
                                          MESSAGES['NO_ORDER'],
                                          parse_mode='html',
                                          reply_markup=self.keyboard.categories_btn())

            elif message.text in (config_bot.KEYBOARDS['UP'], config_bot.KEYBOARDS['DOWN']):
                logger.debug(f'Пользователь: {message.from_user.id} нажал "вверх/вниз" для изменения количества товара в заказе')
                self.pressed_up_down_btn(message)

            elif message.text in (config_bot.KEYBOARDS['PREVIOUS'], config_bot.KEYBOARDS['NEXT']):
                logger.debug(f'Пользователь: {message.from_user.id} нажал "вперед/назад" для просмотра своих заказов')
                self.pressed_next_previous_btn(message)

            elif message.text == config_bot.KEYBOARDS['X']:
                logger.debug(f'Пользователь: {message.from_user.id} нажал "удалить товар из заказа"')
                self.pressed_delete_btn(message)

            elif message.text == config_bot.KEYBOARDS['APPLY']:
                logger.debug(f'Пользователь: {message.from_user.id} нажал "оформить заказ"')
                self.pressed_apply_order_btn(message)

            # START ADMIN PANEL HANDLER

            elif message.text == config_bot.ADMIN_KEYBOARDS['ORDERS_LIST']:
                logger.debug(f'Пользователь в админке: {message.from_user.id} нажал "список заказов"')
                self.pressed_orders_list_btn(message)

            elif message.text == config_bot.ADMIN_KEYBOARDS['SEARCH_ORDER']:
                logger.debug(f'Пользователь в админке: {message.from_user.id} нажал "поиск заказа по user_id"')
                self.pressed_search_order_btn(message)

            elif message.text == config_bot.ADMIN_KEYBOARDS['PRODUCTS_LIST']:
                logger.debug(f'Пользователь в админке: {message.from_user.id} нажал "список продуктов"')
                self.pressed_product_list_btn(message)

            elif message.text == config_bot.ADMIN_KEYBOARDS['CATEGORIES_LIST']:
                logger.debug(f'Пользователь в админке: {message.from_user.id} нажал "список категорий"')
                self.pressed_categories_list_btn(message)

            elif message.text == config_bot.ADMIN_KEYBOARDS['CREATE_CATEGORY']:
                logger.debug(f'Пользователь в админке: {message.from_user.id} нажал "создать категорию"')
                self.pressed_create_category_btn(message)

            elif message.text == config_bot.ADMIN_KEYBOARDS['CREATE_PRODUCT']:
                logger.debug(f'Пользователь в админке: {message.from_user.id} нажал "создать продукт"')
                self.pressed_create_product(message)

            elif message.text == config_bot.KEYBOARDS['ADD_PRODUCT']:
                logger.debug(f'Пользователь в админке: {message.from_user.id} нажал "Добавить продукт на складе"')
                self.pressed_add_product(message)

            elif message.text == config_bot.KEYBOARDS['DELETE_PRODUCT']:
                logger.debug(f'Пользователь в админке: {message.from_user.id} нажал "Удалить продукт"')
                self.pressed_delete_product(message)

            elif message.text == config_bot.KEYBOARDS['BACK']:
                logger.debug(f'Пользователь в админке: {message.from_user.id} нажал "назад"')
                self.pressed_back_admin_btn(message)

            else:
                logger.debug(f'Пользователь: {message.from_user.id} нажал неизвестную команду в {datetime.datetime.now()}')
                self.bot.send_message(message.from_user.id,
                                      MESSAGES['UNDEFINED'],
                                      reply_markup=self.keyboard.start_menu())
