from settings.config_bot import KEYBOARDS

about_text = """
    Приветсвуем в <b>нашем</b> магазине!
"""


settings_text = f"""
    Общее руководство по боту:
    Навигация:
    {KEYBOARDS['<<']} - назад
    {KEYBOARDS['>>']} - вперед
"""

product_text = """Наименование товара: {}

Цена товара: {} руб.
Количество в заказе: {} шт.
Остаток на складе: {}
    
Товар успешно добавлен в заказ
"""

no_order_text = """
    <i>Список заказов пуст</i>
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
    Итоговая стоимость: {} руб.
    
    Спасибо,что выбрали нашу компанию ☺️

"""

undefined_text = """
К сожалению, я вас не понимаю
Пожалуйста выберите нужный вам раздел по кнопке ниже
"""

MESSAGES = {
    'ABOUT': about_text,
    'SETTINGS': settings_text,
    'PRODUCT': product_text,
    'NO_ORDER': no_order_text,
    'ORDER': order_text,
    'PRODUCT_POSITION': product_position_text,
    'APPLY_ORDER': apply_order_text,
    'UNDEFINED': undefined_text
}
