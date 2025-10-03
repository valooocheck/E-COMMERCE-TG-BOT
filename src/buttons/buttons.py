from pydantic import BaseModel

NOT_ADMIN = "Вы не являетесь администратором! 🚫 Доступ запрещен! 😠"
ANSWER_ADMIN = "Это меню администратора 👑, выбери из предложенного! 📋"
ANSWER_ADD_CATEGORY = 'Категория "%s" успешно добавлена! ✅'

RECORD_NOT_FOUND = "Запись не найдена. 😔"
RECORDS_NOT_FOUND = "Записи не найдены. 😔"

ANSWER_CONFLICT_ADD = 'Имя "%s" уже существует! ⚠️'

NAME_ADD_PRODUCT = "Введите название товара! 🏷️📝"
DESCRIPTION_ADD_PRODUCT = "Введите описание товара! 📝📋"

ANSWER_CANCEL = "Действие отменено. 😔"

NAME_ADD_CATEGORY = "Введите название категории! 🏷️📝"
UPDATE_CATEGORY = "📂 Выберите категорию, которую хотите изменить"
DELETE_CATEGORY = "🗑️ Выберите категорию, которую хотите удалить"

SUCCESS_UPDATE_CATEGORY = 'Категория изменена на "%s". ✅'
SUCCESS_DELETE_CATEGORY = "Категория успешно удалена! ✅"
ERROR_DUPLICATE_NAME = "Такое имя уже существует. Попробуйте другое имя. ⚠️"
ERROR_EMPTY_NAME = "Имя не может быть пустым. Попробуйте снова. 😔"
VERIFY_NAME = "✏️ Текущее имя: %s \nВведите новое имя категории:"
VERIFY_DELETE_CAT = '🗑️ Действительно хотите удалить категорию "%s"? Подтвердите:'
VERIFY_UPDATE_CAT = '✏️ Вы действительно хотите изменить на "%s"? Подтвердите:'

CATEGORY_FOR_PRODUCT = "📂 Выберите категорию для нового товара!"
PRICE_FOR_PRODUCT = "💰 Введите цену для нового товара!"
PHOTO_FOR_PRODUCT = "📸 Пришлите фотографию товара!"
PHOTO_NOT_FOR_PRODUCT = "📸 Вы не прислали фотографию товара! \nПопробуйте еще раз! ⚠️"
VERIFY_ADD_PRODUCT = "➕ Вы действительно хотите добавить товар? Подтвердите:"
SUCCESS_ADD_PRODUCT = "Товар успешно добавлен! ✅"
CHOOSE_CATEGORY_DELETE_PRODUCT = "📂 Выберите из какой категории вы хотите удалить товар"
CHOOSE_DELETE_PRODUCT = "🗑️ Выберите товар для удаления!"
VERIFY_DELETE_PRODUCT = "🗑️ Вы действительно хотите удалить товар? Подтвердите:"
SUCCESS_DELETE_PRODUCT = "Товар успешно удален! ✅"

CHOOSE_CATEGORY_UPDATE_PRODUCT = "📂 Выберите из какой категории вы хотите изменить товар"
CHOOSE_UPDATE_PRODUCT = "✏️ Выберите товар для изменения!"
CHOOSE_UPDATE_PRODUCT_ATTRIBUTE = "✏️ Выберите какое поле вы хотите изменить!"
ANSWER_FOR_UPDATE_ATTR = "✏️ Текущее значение: %s\nВведите новое значение, которое хотите установить"
ERROR_UPDATE_ATTR = "Что-то пошло не так, отправь сообщение еще раз! ⚠️"
UPDATE_PHOTO = "📸 Пришлите новое фото для товара"
VERIFY_UPDATE_PHOTO = "📸 Вы действительно хотите изменить фото? Подтвердите:"
SUCCESS_UPDATE_PRODUCT = "Товар успешно обновлен! ✅"
CHOOSE_CATEGORY_FOR_UPDATE_PRODUCT = "📂 Выберите какую категорию вы хотите установить у товара!"
VERIFY_UPDATE_CAT_IN_PROD = '✏️ Вы действительно хотите изменить категорию на "%s"? Подтвердите:'

NAME_USER_ADMIN_ADD = "👤 Введите имя пользователя для добавления администратора"
ANSWER_NOT_FOUND_USER = "❌ Пользователь не найден или не пользуется сервисом\nПопробуйте ввести имя ещё раз"
ANSWER_ADMIN_ERROR_PRICE = "💰 Некорректный формат цены\nВведите цену ещё раз"

HELLO_CLIENT = "👋 Привет, @%s! Выбери пункт из меню"

CATEGORY_CHOOSE = "📂 Выберите категорию"
CHOOSE_PRODUCT = "📦 Выберите товар для просмотра"

SUCCESS_ADD_ADMIN = "Теперь пользователь @%s администратор! 👑"

ANSWER_NOT_PRODUCT = "❌ К сожалению, такой товар не найден"
ANSWER_ADD_CART = "🛒 Товар успешно добавлен в корзину!"

EMPTY_CART = "🛒 Ваша корзина пуста! Добавьте товары! \n Введите команду /start."

NO_ADDRESS = "🏠 У вас нет сохраненных адресов. Давайте добавим новый адрес для доставки.\n\nВведите полный адрес (страна, город, улица, дом, квартира, индекс):"
SELECT_ADDRESS = "📍 Выберите адрес для доставки:"
ADDRESS_NOT_FOUND = "Адреса не найдены. 😔"
SUCCESS_ADD_ADDRESS = "Адрес добавлен! Теперь выберите адрес для заказа. ✅"
ENTER_ADDRESS = "🏠 Введите адрес:"


ORDER_NOT_FOUND = "Заказ не найден! 😔"
ORDER_UPDATE_STATUS = "📋 Введите новый статус для заказа!"
SUCCESS_UPDATE_STATUS = "Статус заказа успешно обновлен! ✅"
NO_ORDERS_MESSAGE = "У вас пока нет заказов. 😔\n\nВы можете сделать заказ через меню. \n /start"


class Buttons(BaseModel):
    add_admin: str = "🚀 Добавить администратора"
    add_category: str = "🔗 Добавить категорию"
    update_category: str = "✏️ Редактировать категорию"
    delete_category: str = "🗑️ Удалить категорию"
    add_product: str = "➕ Добавить товар"
    update_product: str = "✏️ Редактировать товар"
    delete_product: str = "🗑️ Удалить товар"
    cancel: str = "❌ Отмена"
    confirm: str = "✅ Подтвердить"
    show_catalog: str = "📚 Показать каталог"
    next_product: str = "➡️ Следующий товар"
    previous_product: str = "⬅️ Предыдущий товар"
    add_basket: str = "🛒 Добавить в корзину"
    delete_basket: str = "🗑️ Удалить из корзины"
    show_cart: str = "🛒 Показать корзину"
    place_order: str = "💳 Оформить заказ"
    delete_item_cart: str = "🗑️ Удалить товар из корзины"
    add_address: str = "🏠 Добавить новый адрес"
    viewing_orders: str = "📋 Посмотреть заказы"
    show_orders: str = "📦 Мои заказы"


CARD_TEMPLATE = """
<b>📦 Название:</b> %s
<b>💰 Цена:</b> %s₽
<b>📝 Описание:</b> %s
<b>🏷️ Категория:</b> %s
<b>📊 В наличии:</b> %s шт.
"""


buttons = Buttons()
