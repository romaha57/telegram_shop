from loguru import logger


class Logger:

    @staticmethod
    def debug_only(record):
        """Функция для фильтрации записи в логи только для уровня DEBUG"""

        return record["level"].name == 'DEBUG'

    @staticmethod
    def warning_only(record):
        """Функция для фильтрации записи в логи только для уровня WARNING"""

        return record["level"].name == 'WARNING'

    def debug_log_write(self):
        """Записывает в debug.log служебные сообщения"""

        logger.add('debug.log', format="{time} {level} {message}", level="DEBUG", rotation="50 KB",
                   compression="zip", filter=self.debug_only)

    def warning_log_write(self):
        """Записывает в warning.log сообщения об ошибках"""

        logger.add('warning.log', format="{time} {level} {message}", level="WARNING", rotation="50 KB",
                   compression="zip", filter=self.warning_only)

    def run_logging(self) -> None:
        """Запускает функцию до старта бота для начала логирования"""

        self.debug_log_write()
        self.warning_log_write()
