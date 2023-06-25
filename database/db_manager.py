import os.path

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.all_models import Base, Category, Order, Product
from settings import config_bot
from settings.utils import convert_to_list_id


class Singleton(type):
    """Синглтон для БД"""

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class DBManager(metaclass=Singleton):

    def __init__(self):
        """Подключение к БД и создание таблиц в ней"""

        self.engine = create_engine(config_bot.DATABASE)
        Session = sessionmaker(self.engine, autoflush=False)
        self.session = Session()

        logger.debug('Подключение к БД успешно')

        if not os.path.isfile(config_bot.DATABASE):
            Base.metadata.create_all(self.engine)
            logger.debug('Создание таблиц в БД и подключение')

    def get_product_by_id(self, product_id):
        """Получаем продукт по его id"""

        product = self.session.query(Product).get(product_id)

        return product

    def get_products_by_category(self, category_name):
        """Получаем продукт по его категории"""

        category_id = self.session.query(Category).filter_by(name=category_name).first().id
        products = self.session.query(Product).filter_by(category_id=category_id).all()

        return products

    def get_all_categories(self):
        """Получаем все категории, в которых есть товары"""

        products_with_distinct_cat_id = self.session.query(Product).distinct(Product.category_id). \
            group_by(Product.category_id).all()

        distinct_cat_id = [i.category_id for i in products_with_distinct_cat_id]
        categories = self.session.query(Category).filter(Category.id.in_(distinct_cat_id))

        return categories

    def create_order(self, product_id, user_id):
        """Создание заказа"""

        user_products_id = self.get_users_card(user_id=user_id)

        # если данный товар уже есть в заказах пользователя, то увеличиваем его количество в заказе
        if int(product_id) in user_products_id:
            order = self.session.query(Order).filter_by(user_id=user_id, product_id=product_id).first()
            order.quantity += 1

            self.update_product_in_stock(product_id=product_id)
            self.session.commit()
            self.session.close()

        # создаем новый заказ, если такого товара у пользователя нет в заказах
        else:
            order = Order(
                product_id=product_id,
                quantity=1,
                user_id=user_id,
            )
            self.session.add(order)

            self.update_product_in_stock(product_id=product_id)
            self.session.commit()
            self.session.close()

    def update_product_in_stock(self, product_id):
        """Убавляем товар на складе на 1 единицу"""

        product = self.session.query(Product).filter_by(id=product_id).first()
        product.quantity -= 1

    def add_product_in_stock(self, product_id):
        """Увеличиваем товар на складе на 1 единицу"""

        product = self.session.query(Product).filter_by(id=product_id).first()
        product.quantity += 1

    def get_users_card(self, user_id):
        """Получаем список product_id всех заказов данного пользователя по user_id из телеграма"""

        user_products_card = self.session.query(Order.product_id).filter_by(user_id=user_id).all()

        return convert_to_list_id(user_products_card)

    def get_count_product_in_orders(self, product_id, user_id):
        """Получаем количество данного товара по его product_id в заказах пользователя по user_id"""

        count_products = self.session.query(Order).filter_by(user_id=user_id, product_id=product_id).first().quantity

        return count_products

    def increase_quantity_product_in_order(self, product_id, user_id):
        """Получаем заказ для данного пользователя и конкретного продукта и увеличиваем количества на 1 единицу"""

        order = self.session.query(Order).filter_by(user_id=user_id, product_id=product_id).first()
        order.quantity += 1
        self.session.commit()

    def decrease_quantity_product_in_order(self, product_id, user_id):
        """Получаем заказ для данного пользователя и конкретного продукта и уменьшаем количества на 1 единицу"""

        order = self.session.query(Order).filter_by(user_id=user_id, product_id=product_id).first()
        order.quantity -= 1
        self.session.commit()

    def has_order(self, user_id):
        """Проверяем есть ли заказ у данного пользователя"""

        return self.session.query(Order).filter_by(user_id=user_id).count()

    def get_total_product_price(self, product, user_id):
        """Получаем полную стоимость товара в заказе с учетом его количества"""
        count = self.get_count_product_in_orders(product_id=product.id, user_id=user_id)

        return product.price * count

    def get_count_products_in_order(self, user_id):
        """Получаем количество позиции в заказе данного пользователя"""

        return self.session.query(Order).filter_by(user_id=user_id).count()

    def get_total_cost_order_by_user(self, user_id):
        """Получаем итоговую стоимость всех заказов"""

        total_cost = 0
        orders = self.session.query(Order).filter_by(user_id=user_id).all()
        for order in orders:
            product = self.session.query(Product).filter_by(id=order.product_id).first()
            total_cost += product.price * order.quantity

        return total_cost

    def delete_product_in_order(self, product_id, user_id):
        """Удаляем товар из заказа пользоваля после нажатия кнопки 'X' """

        self.session.query(Order).filter_by(user_id=user_id, product_id=product_id).delete()
        self.session.commit()
        self.session.close()

    def delete_order(self, user_id):
        """Удаляем заказы пользователя после оформления"""

        orders = self.session.query(Order).filter_by(user_id=user_id).all()
        for order in orders:
            self.session.delete(order)
            self.session.commit()
        self.session.close()
