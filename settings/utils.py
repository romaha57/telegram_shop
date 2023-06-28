from sqlite3 import Row

from models.all_models import Product


def convert_to_list_id(products_list: list[Row(Product)]) -> list[int]:
    """Конвертируем из списка из БД в список product_id(int)"""

    return [product[0] for product in products_list]
