from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from buttons.buttons import ANSWER_CONFLICT_ADD_CATEGORY, DELETE_CATEGORY, UPDATE_CATEGORY, buttons
from common.exceptions import Conflict, UpdateDatabaseError
from db import db_manager
from db.session_manager import DatabaseSessionManager
from handlers.v1.admin.admin import cancel_keyboard
from models.models import CategoriesOrm


class MixinCategoryStates(StatesGroup):
    confirming = State()
    selecting_category = State()


class AddProductStates(StatesGroup):
    waiting_for_name = State()


class EditCategoryStates(MixinCategoryStates):
    entering_new_name = State()


class DeleteCategoryStates(MixinCategoryStates):
    pass


def get_confirm_keyboard(confirm):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=confirm)],
            # [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_edit")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
        ]
    )


class CategoriesService:
    def __init__(self, db_man: DatabaseSessionManager, table) -> None:
        self.db_manager = db_man
        self.table = table

    async def add(self, data):
        new_record = self.table(name=data)
        try:
            await new_record.save(self.db_manager)
        except Conflict:
            raise Conflict(ANSWER_CONFLICT_ADD_CATEGORY % data) from None
        return new_record

    async def _get_all(self):
        return await self.table.find_all(self.db_manager)

    async def _get_category_in_keyboard(self, callback: CallbackQuery, callback_data: str):
        categories = await self._get_all()

        if not categories:
            await callback.message.answer("Категории не найдены. 😔")
            await callback.answer()
            return

        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        for category in categories:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=category.name,
                        callback_data=f"{callback_data}{category.id}",
                    )
                ]
            )

        keyboard.inline_keyboard.append([InlineKeyboardButton(text=buttons.cancel, callback_data="cancel")])
        return keyboard

    async def delete_category(self, callback: CallbackQuery, state: FSMContext):
        keyboard = await self._get_category_in_keyboard(callback, "delete_select_category_")

        await callback.message.answer(DELETE_CATEGORY, reply_markup=keyboard)
        await callback.answer()

    async def update_category(self, callback: CallbackQuery, state: FSMContext):
        keyboard = await self._get_category_in_keyboard(callback, "select_category_")

        await callback.message.answer(UPDATE_CATEGORY, reply_markup=keyboard)
        # await state.set_state(AddProductStates.waiting_for_name)
        await callback.answer()

    async def _save_record_in_state(self, callback: CallbackQuery, state: FSMContext):
        category_id = callback.data.split("_")[-1]

        category = await self.table.find_by_id(self.db_manager, int(category_id))
        if not category:
            await callback.message.answer("Категория не найдена. 😔")
            await callback.answer()

        await state.update_data(selected_category=category.id)
        return category

    async def select_category_for_delete(self, callback: CallbackQuery, state: FSMContext):
        category = await self._save_record_in_state(callback, state)
        if not category:
            return
        await callback.message.answer(
            f'Действительно хотите удалить категорию "{category.name}"? Подтвердите:',
            reply_markup=get_confirm_keyboard("confirm_delete"),
        )
        await state.set_state(DeleteCategoryStates.confirming)
        await callback.message.delete()

    async def select_category_for_update(self, callback: CallbackQuery, state: FSMContext):
        category = await self._save_record_in_state(callback, state)
        if not category:
            return

        await callback.message.answer(
            f"Текущее имя: {category.name}\nВведите новое имя категории:", reply_markup=cancel_keyboard
        )
        await state.set_state(EditCategoryStates.entering_new_name)
        await callback.answer()
        await callback.message.delete()

    async def enter_new_name(self, message: types.Message, state: FSMContext):
        new_name = message.text.strip()
        if not new_name:
            await message.answer("Имя не может быть пустым. Попробуйте снова.", reply_markup=cancel_keyboard)
            await state.set_state(EditCategoryStates.entering_new_name)

            return

        await state.update_data(new_name=new_name)

        await message.answer(
            f"Вы хотите изменить на '{new_name}'? Подтвердите:", reply_markup=get_confirm_keyboard("confirm_edit")
        )
        await state.set_state(EditCategoryStates.confirming)
        await message.delete()

    async def confirmation_delete(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        category_id = data["selected_category"]
        await self.table.delete_by_id(db_manager=self.db_manager, record_id=int(category_id))
        await callback.message.answer("Категория успешно удалена!'. ✅", reply_markup=None)
        await state.clear()
        await callback.answer()
        await callback.message.delete()

    async def confirmation_changes(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        category_id = data["selected_category"]
        new_name = data["new_name"]

        try:
            new_category = await self.table.update_by_id(
                db_manager=self.db_manager, record_id=int(category_id), name=new_name
            )
            await callback.message.answer(f"Категория изменена на '{new_category.name}'. ✅", reply_markup=None)
        except Conflict as e:
            await callback.message.answer(f"Ошибка: {e.args[0]}. Попробуйте другое имя.", reply_markup=None)
        except UpdateDatabaseError:
            await callback.message.answer("Такое имя уже существует. Попробуйте другое имя.", reply_markup=None)
            await state.set_state(EditCategoryStates.entering_new_name)
            await callback.answer()
            return
        except Exception as e:
            await callback.message.answer(f"Неизвестная ошибка: {e}. Попробуйте позже.", reply_markup=None)

        await state.clear()
        await callback.answer()
        await callback.message.delete()


categories_tg_service = CategoriesService(db_manager, CategoriesOrm)
