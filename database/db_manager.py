import os.path
from typing import Type

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

    def get_product_by_id(self, product_id: int) -> Product:
        """Получаем продукт по его id"""

        product = self.session.query(Product).get(product_id)

        return product

    def get_products_by_category(self, category_name: str) -> list[Type[Product]]:
        """Получаем продукт по его категории"""

        category_id = self.session.query(Category).filter_by(name=category_name).first().id
        products = self.session.query(Product).filter_by(category_id=category_id).all()

        return products

    def get_all_categories_with_product(self) -> list[Type[Category]]:
        """Получаем все категории, в которых есть товары"""

        products_with_distinct_cat_id = self.session.query(Product).distinct(Product.category_id). \
            group_by(Product.category_id).all()

        distinct_cat_id = [i.category_id for i in products_with_distinct_cat_id]
        categories = self.session.query(Category).filter(Category.id.in_(distinct_cat_id)).all()

        return categories

    def get_all_products(self) -> list[Type[Product]]:
        """Получаем все продукты для админки"""

        return self.session.query(Product).all()

    def get_all_categories(self) -> list[Type[Category]]:
        """Получаем все категории для админки"""

        return self.session.query(Category).all()

    def get_category_by_id(self, category_id: int) -> Type[Category]:
        """Получаем категорию по ее id"""

        return self.session.query(Category).filter_by(id=category_id).first()

    def create_order(self, product_id: int, user_id: int) -> None:
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

    def update_product_in_stock(self, product_id: int) -> None:
        """Убавляем товар на складе на 1 единицу"""

        product = self.session.query(Product).filter_by(id=product_id).first()
        product.quantity -= 1

    def add_product_in_stock(self, product_id: int) -> None:
        """Увеличиваем товар на складе на 1 единицу"""

        product = self.session.query(Product).filter_by(id=product_id).first()
        product.quantity += 1

    def get_users_card(self, user_id: int) -> list[int]:
        """Получаем список product_id из всех заказов данного пользователя по user_id из телеграма"""

        user_products_card = self.session.query(Order.product_id).filter_by(user_id=user_id).all()

        return convert_to_list_id(user_products_card)

    def get_count_product_in_orders(self, product_id: int, user_id: int) -> int:
        """Получаем количество данного товара по его product_id в заказах пользователя по user_id"""

        count_products = self.session.query(Order).filter_by(user_id=user_id, product_id=product_id).first().quantity

        return count_products

    def increase_quantity_product_in_order(self, product_id: int, user_id: int) -> None:
        """Получаем заказ для данного пользователя и конкретного продукта и увеличиваем количества на 1 единицу"""

        order = self.session.query(Order).filter_by(user_id=user_id, product_id=product_id).first()
        order.quantity += 1
        self.session.commit()

    def decrease_quantity_product_in_order(self, product_id: int, user_id: int) -> None:
        """Получаем заказ для данного пользователя и конкретного продукта и уменьшаем количества на 1 единицу"""

        order = self.session.query(Order).filter_by(user_id=user_id, product_id=product_id).first()
        order.quantity -= 1
        self.session.commit()

    def has_order(self, user_id: int) -> bool:
        """Проверяем есть ли заказ у данного пользователя"""

        return bool(self.session.query(Order).filter_by(user_id=user_id).count())

    def get_total_product_price(self, product: Product, user_id: int) -> int:
        """Получаем полную стоимость товара в заказе с учетом его количества"""
        count = self.get_count_product_in_orders(product_id=product.id, user_id=user_id)

        return product.price * count

    def get_count_products_in_order(self, user_id: int) -> int:
        """Получаем количество позиции в заказе данного пользователя"""

        return self.session.query(Order).filter_by(user_id=user_id).count()

    def get_total_cost_order_by_user(self, user_id: int) -> int:
        """Получаем итоговую стоимость всех заказов"""

        total_cost = 0
        orders = self.session.query(Order).filter_by(user_id=user_id).all()
        for order in orders:
            product = self.session.query(Product).filter_by(id=order.product_id).first()
            total_cost += product.price * order.quantity

        return total_cost

    def order_by_user_and_product(self, user_id: int, product_id: int) -> Type[Order]:
        """Получаем конкретный заказ для пользователя и продукта"""

        return self.session.query(Order).filter_by(user_id=user_id, product_id=product_id).first()

    def delete_product_in_order(self, product_id: int, user_id: int) -> None:
        """Удаляем товар из заказа пользователя после нажатия кнопки 'X' """

        self.session.query(Order).filter_by(user_id=user_id, product_id=product_id).delete()
        self.session.commit()
        self.session.close()

    def delete_order(self, user_id: int) -> None:
        """Удаляем заказы пользователя после оформления"""

        orders = self.session.query(Order).filter_by(user_id=user_id).all()
        for order in orders:
            self.session.delete(order)
            self.session.commit()
        self.session.close()

    def get_all_orders(self) -> list[Type[Order]]:
        """Получение всех заказов для админки"""

        return self.session.query(Order).all()

    def create_category(self, name: str) -> None:
        """Создание категории через админку"""

        category = Category(
            name=name
        )
        self.session.add(category)
        self.session.commit()

    def create_product(self, data: dict) -> Product:
        """Создание продукта через админку"""

        product = Product(
            name=data['product_name'],
            price=data['product_price'],
            quantity=data['product_quantity'],
            category_id=data['product_category_id'],
        )
        self.session.add(product)
        self.session.commit()

        return product

    def find_category_without_button(self) -> str:
        """Получаем те категории, у которых нет кнопок в настройках бота(settings.config_bot)"""

        result = []
        all_categories = self.session.query(Category.name).all()
        all_categories_in_config = [name.lower() for name in config_bot.CATEGORIES_LIST]
        for category in all_categories:
            if category[0].lower() not in all_categories_in_config:
                result.append(category[0].lower())

        return '\n'.join(result)

    def has_product(self, product_id: int) -> bool:
        """Проверяем есть ли такой id продукта в БД"""

        return bool(self.session.query(Product).filter_by(id=int(product_id)).first())

    def add_product_quantity(self, data: dict) -> None:
        """Добавляем количество товара через админку"""

        product = self.get_product_by_id(product_id=data['product_id'])
        product.quantity += int(data['product_quantity'])
        self.session.commit()

    def delete_product(self, product_id: int) -> None:
        """Удаляем товар через админку"""

        self.session.query(Product).filter_by(id=product_id).delete()
        self.session.commit()
