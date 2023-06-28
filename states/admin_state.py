from telebot.handler_backends import State, StatesGroup


class AdminSignInState(StatesGroup):
    """Состояния для входа в админку"""

    password = State()


class SearchState(StatesGroup):
    """Состояния для поиска заказа"""

    user_id = State()


class CreateCategoryState(StatesGroup):
    """Состояния для создания категории товара"""

    name = State()


class CreateProductState(StatesGroup):
    """Состояния для создания товара"""

    name = State()
    price = State()
    quantity = State()
    category_id = State()


class AddProductState(StatesGroup):
    """Состояния для добавления продукта на склад"""

    id = State()
    quantity = State()


class DeleteProductState(StatesGroup):
    """Состояние для удаления продукта из админки"""

    id = State()
