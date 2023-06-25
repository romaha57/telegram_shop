def convert_to_list_id(products_list):
    """Конвертируем из списка из БД в список product_id(int)"""

    return [product[0] for product in products_list]
