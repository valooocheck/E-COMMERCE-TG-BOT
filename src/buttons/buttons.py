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
UPDATE_CATEGORY = "Выберите категорию, которую хотите изменить"
DELETE_CATEGORY = "Выберите категорию, которую хотите удалить"

SUCCESS_UPDATE_CATEGORY = 'Категория изменена на "%s". ✅'
SUCCESS_DELETE_CATEGORY = "Категория успешно удалена!. ✅"
ERROR_DUPLICATE_NAME = "Такое имя уже существует. Попробуйте другое имя."
ERROR_EMPTY_NAME = "Имя не может быть пустым. Попробуйте снова."
VERIFY_NAME = "Текущее имя: %s \nВведите новое имя категории:"
VERIFY_DELETE_CAT = 'Действительно хотите удалить категорию "%s"? Подтвердите:'
VERIFY_UPDATE_CAT = 'Вы действительно хотите изменить на "%s"? Подтвердите:'

CATEGORY_FOR_PRODUCT = "Выберите категорию для нового товара!"
PRICE_FOR_PRODUCT = "Введите цену для нового товара!"
PHOTO_FOR_PRODUCT = "Пришлите фотографию товара!!"
PHOTO_NOT_FOR_PRODUCT = "Вы не прислали фотографию товара!! \nПопробуйте еще раз!"
VERIFY_ADD_PRODUCT = "Вы действительно хотите добавить товар? Подтвердите:"
SUCCESS_ADD_PRODUCT = "Товар успешно добавлен!"
CHOOSE_CATEGORY_DELETE_PRODUCT = "Выберите из какой категории вы хотите удалить товар"
CHOOSE_DELETE_PRODUCT = "Выберите товар для удаления!"
VERIFY_DELETE_PRODUCT = "Вы действительно хотите удалить товар? Подтвердите:"
SUCCESS_DELETE_PRODUCT = "Товар успешно удален!"


class Buttons(BaseModel):
    add_admin: str = "🚀  Добавить администратора!"
    add_category: str = "🔗 Добавить категорию!"
    update_category: str = "⏰ Редактировать категорию!"
    delete_category: str = "⏰ Удалить категорию!!"
    add_product: str = "➕ Добавить товар!"
    update_product: str = "⏰ Редактировать товар!"
    delete_product: str = "❌ Удалить товар!"
    cancel: str = "❌ Отмена"
    confirm: str = "✅ Подтвердить"


buttons = Buttons()
