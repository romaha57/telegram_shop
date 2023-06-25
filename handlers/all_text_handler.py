import datetime

from loguru import logger

from handlers.handler import Handler
from settings import config_bot
from settings.messages import MESSAGES


class AllTextHandler(Handler):

    def __init__(self, bot):
        super().__init__(bot)

    def pressed_about_btn(self, message):
        """При нажатии кнопки 'О магазине' """

        self.bot.send_message(message.from_user.id,
                              MESSAGES['ABOUT'],
                              parse_mode='html',
                              reply_markup=self.keyboard.back_btn())

    def pressed_back_btn(self, message):
        """При нажатии кнопки 'назад' """

        self.bot.send_message(message.from_user.id,
                              'Вы вернулись назад',
                              reply_markup=self.keyboard.start_menu())

    def pressed_settings_btn(self, message):
        """При нажатии кнопки 'Настройки' """

        self.bot.send_message(message.from_user.id,
                              MESSAGES['SETTINGS'],
                              parse_mode='html',
                              reply_markup=self.keyboard.back_btn())

    def pressed_choose_good_btn(self, message):
        """При нажатии кнопки 'Выбрать товар' """

        self.bot.send_message(message.from_user.id,
                              'Каталог товаров',
                              reply_markup=self.keyboard.categories_btn())

    def pressed_product_btn(self, message):
        """При нажатии кнопки выбора категории """

        self.bot.send_message(message.from_user.id,
                              f'Выбрана категория: <b>{message.text}</b>',
                              parse_mode='html',
                              reply_markup=self.keyboard.get_product_button(message.text.split()[1]))

    def pressed_order_btn(self, message):
        """При нажатии кнопки 'Заказ' """

        self.step = 0
        products_id_in_order = self.db.get_users_card(user_id=message.from_user.id)
        product = self.db.get_product_by_id(products_id_in_order[self.step])

        self.send_message_order_item(message=message, product=product)

    def send_message_order_item(self, message, product):
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

    def pressed_up_down_btn(self, message):
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

    def pressed_next_previous_btn(self, message):
        """При нажатии кнопки 'Предыдущий/Следующий товар в заказе' """

        if message.text == config_bot.KEYBOARDS['NEXT'] and self.step < self.db.get_count_products_in_order(user_id=message.from_user.id) - 1:
            self.step += 1
        elif message.text == config_bot.KEYBOARDS['PREVIOUS'] and self.step != 0:
            self.step -= 1

        products_id_in_order = self.db.get_users_card(user_id=message.from_user.id)
        product = self.db.get_product_by_id(products_id_in_order[self.step])

        self.send_message_order_item(message, product)

    def pressed_delete_btn(self, message):
        products_id_in_order = self.db.get_users_card(user_id=message.from_user.id)
        product = self.db.get_product_by_id(products_id_in_order[self.step])
        product_name = product.name

        if products_id_in_order:
            self.db.delete_product_in_order(product_id=product.id, user_id=message.from_user.id)

            self.bot.send_message(message.from_user.id,
                                  f'Товар <b>{product_name}</b> удален из заказа',
                                  parse_mode='html')

    def pressed_apply_order_btn(self, message):
        self.bot.send_message(message.from_user.id,
                              MESSAGES['APPLY_ORDER'].format(
                                  self.db.get_total_cost_order_by_user(user_id=message.from_user.id)
                              ),
                              reply_markup=self.keyboard.categories_btn(),
                              parse_mode='html')
        logger.debug(f'Пользователь {message.from_user.id} оформил заказ в {datetime.datetime.now()}')
        self.db.delete_order(user_id=message.from_user.id)
        logger.debug(f'У пользователя {message.from_user.id} очищена корзина в  {datetime.datetime.now()}')

    def handle(self):
        @self.bot.message_handler(func=lambda message: True)
        def all_text(message):
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

            elif message.text in (config_bot.KEYBOARDS['MACBOOK'], config_bot.KEYBOARDS['IPHONE'], config_bot.KEYBOARDS['APPLEWATCH']):
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

            else:
                logger.debug(f'Пользователь: {message.from_user.id} нажал неизвестную команду')
                self.bot.send_message(message.from_user.id,
                                      MESSAGES['UNDEFINED'],
                                      reply_markup=self.keyboard.start_menu())
