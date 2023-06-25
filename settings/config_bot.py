import os.path

from emoji import emojize
from dotenv import load_dotenv, find_dotenv
from loguru import logger


if not find_dotenv():
    logger.warning('Переменные окружения не найдены')
elif load_dotenv():
    BOT_TOKEN = os.getenv('BOT_TOKEN')

DB_NAME = os.getenv('DB_NAME')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join('sqlite:///' + BASE_DIR, DB_NAME)

COUNT = 0

KEYBOARDS = {
    'CHOOSE_GOODS': emojize(':open_file_folder: Выбрать товар'),
    'ABOUT': emojize(':speech_balloon: О магазине'),
    'SETTINGS': emojize('⚙️ Настройки'),
    'IPHONE': emojize(':mobile_phone: iPhone'),
    'MACBOOK': emojize(':laptop: MacBook'),
    'APPLEWATCH': emojize(':watch: AppleWatch'),
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
    'COPY': '©️'
}
