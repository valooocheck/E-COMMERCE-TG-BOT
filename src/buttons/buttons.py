from pydantic import BaseModel

NOT_ADMIN = "Вы не являетесь администратором! 🚫 Доступ запрещен! 😠"
ANSWER_ADMIN = "Это меню администратора 👑, выбери из предложенного! 📋"
ANSWER_ADD_CATEGORY = 'Категория "%s" успешно добавлена! ✅'
ANSWER_CONFLICT_ADD_CATEGORY = 'Категория "%s" уже существует! ⚠️'


ANSWER_CANCEL = "Действие отменено. 😔"


NAME_ADD_CATEGORY = "Введите название категории! 🏷️📝"
UPDATE_CATEGORY = "Выберите категорию, которую хотите изменить"
DELETE_CATEGORY = "Выберите категорию, которую хотите удалить"


class Buttons(BaseModel):
    add_admin: str = "🚀  Добавить администратора!"
    add_category: str = "🔗 Добавить категорию!"
    update_category: str = "⏰ Редактировать категорию!"
    delete_category: str = "⏰ Удалить категорию!!"
    add_product: str = "➕ Добавить товар!"
    update_product: str = "⏰ Редактировать товар!"
    cancel: str = "❌ Отмена"


buttons = Buttons()
