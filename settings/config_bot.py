import os.path

from dotenv import find_dotenv, load_dotenv
from emoji import emojize
from loguru import logger

if not find_dotenv():
    logger.warning('Переменные окружения не найдены')
elif load_dotenv():
    BOT_TOKEN = os.getenv('BOT_TOKEN')

DB_NAME = os.getenv('DB_NAME')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join('sqlite:///' + BASE_DIR, DB_NAME)
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

COUNT = 0

CATEGORIES_LIST = {
    'IPHONE': emojize(':mobile_phone: iPhone'),
    'MACBOOK': emojize(':laptop: MacBook'),
    'APPLEWATCH': emojize(':watch: AppleWatch'),
}

KEYBOARDS = {
    'CHOOSE_GOODS': emojize(':open_file_folder: Выбрать товар'),
    'ABOUT': emojize(':speech_balloon: О магазине'),
    'SETTINGS': emojize('⚙️ Настройки'),
    '<<': emojize('⏪'),
    '>>': emojize('⏩'),
    'PREVIOUS': emojize('◀️'),
    'NEXT': emojize('▶️'),
    'ORDER': emojize('✅ ЗАКАЗ'),
    'X': emojize('❌'),
    'DOWN': emojize('🔽'),
    'AMOUNT_PRODUCT': COUNT,
    'AMOUNT_ORDERS': COUNT,
    'UP': emojize('🔼'),
    'APPLY': '✅ Оформить заказ',
    'COPY': '©️',
    'ADD_PRODUCT': emojize(':plus: Добавить продукт на складе'),
    'DELETE_PRODUCT': emojize(':cross_mark: Удалить продукт'),
    'BACK': emojize(':fast_reverse_button: Назад')
}

ADMIN_KEYBOARDS = {
    'ORDERS_LIST': emojize(':ledger: Список заказов'),
    'PRODUCTS_LIST': emojize(':black_small_square: Список продуктов'),
    'CATEGORIES_LIST': emojize(':large_blue_diamond: Список категорий'),
    'CREATE_PRODUCT': emojize(':plus: Создать продукт'),
    'CREATE_CATEGORY': emojize(':check_mark: Создать категорию'),
    'SEARCH_ORDER': emojize(':magnifying_glass_tilted_left: Поиск заказа'),
}
