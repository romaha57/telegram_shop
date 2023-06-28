from settings.config_bot import KEYBOARDS

start_text = """
Приветствуем в магазине техники Apple
Предоставляем качественный товар по хорошим ценам ☺️
"""

about_text = """
    Приветствуем в <b>нашем</b> магазине!
"""


settings_text = f"""
    Общее руководство по боту:
    Навигация:
    {KEYBOARDS['<<']} - <i>назад</i>
    {KEYBOARDS['>>']} - <i>вперед</i>
    {KEYBOARDS['UP']} - <i>добавить количество товара в заказе</i>
    {KEYBOARDS['DOWN']} - <i>убавить количество товара в заказе</i>
    {KEYBOARDS['X']} - <i>удалить товар из заказа</i>
    {KEYBOARDS['PREVIOUS']} - <i>следующий товар в заказе</i>
    {KEYBOARDS['NEXT']} - <i>предыдущий товар в заказе</i>
"""

product_text = """Наименование товара: <b>{}</b>

Цена товара: <b>{}</b> руб.
Количество в заказе: <b>{}</b> шт.
Остаток на складе: <b>{}</b> шт.
    
<b>Товар успешно добавлен в заказ</b>
"""

no_order_text = """
    <i>Список заказов пуст...</i>
"""

order_text = """
    <i>Наименование:</i> {}
    <i>Цена:</i> {} руб.
    <i>Количество:</i> {} шт.
    <i>Остаток на складе:</i> {} шт.
    
    <i>Общая стоимость данной позиции:</i> {} руб.
"""
product_position_text = """
    <i>Позиция в заказе</i> #<b>{}</b>
"""

apply_order_text = """
    <b>Заказ оформлен и передан на склад для сборки</b>
    Итоговая стоимость: <b>{}</b> руб.
    
    Спасибо,что выбрали нашу компанию ☺️

"""

undefined_text = """
К сожалению, я вас не понимаю
Пожалуйста выберите нужный вам раздел по кнопке ниже
Или свяжитесь с администратором
"""

order_info_text = """
ID заказа: <b>{}</b>
ID пользователя: <b>{}</b>
Товар: <b>{}</b>
Количество: <b>{}</b> шт.
Стоимость заказа: <b>{}</b> руб.
Создан: <b>{}</b>

"""

search_result_text = """
Товар: <b>{}</b>
Количество: <b>{}</b> шт.
Цена: <b>{}</b> руб.

Итоговая цена: <b>{}</b> руб.
"""
product_info_text = """
ID: <b>{}</b>
Название: <b>{}</b>
Цена: <b>{}</b> руб.
Количество на складе: <b>{}</b> шт.
Категория: <b>{}</b>
"""

category_info_text = """
ID: <b>{}</b>
Название: <b>{}</b>
"""

add_product_text = """
Количество товара <b>{}</b> увеличено на <b>{}</b> единиц
Итоговое количество: <b>{}</b>
"""

delete_product_text = """
Товар <b>{}</b> успешно удален
"""

notification_text = """
<b>Нужно добавить категории в настройки бота:</b> {}"""

choose_category_text = """
Выбрана категория: <b>{}</b>
"""

delete_product_in_order_text = """
'Товар <b>{}</b> удален из заказа'
"""

total_price_orders_by_user_text = """
    Стоимость всех заказов пользователя с id <b>{}</b>: 
    <b>{}</b> руб.
"""
create_category_text = """
Категория <b>{}</b> успешно создана
"""

MESSAGES = {
    'START': start_text,
    'ABOUT': about_text,
    'SETTINGS': settings_text,
    'PRODUCT': product_text,
    'NO_ORDER': no_order_text,
    'ORDER': order_text,
    'PRODUCT_POSITION': product_position_text,
    'APPLY_ORDER': apply_order_text,
    'UNDEFINED': undefined_text,
    'ORDER_INFO': order_info_text,
    'SEARCH_RESULT': search_result_text,
    'PRODUCT_INFO': product_info_text,
    'CATEGORY_INFO': category_info_text,
    'ADD_PRODUCT': add_product_text,
    'DELETE_PRODUCT': delete_product_text,
    'NOTIFICATION_TEXT': notification_text,
    'CHOOSE_CATEGORY': choose_category_text,
    'DELETE_PRODUCT_IN_ORDER': delete_product_in_order_text,
    'TOTAL_PRICE_ORDERS_BY_USER': total_price_orders_by_user_text,
    'CREATE_CATEGORY': create_category_text,
}
