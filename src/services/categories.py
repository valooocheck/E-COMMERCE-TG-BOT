from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from buttons.buttons import (
    DELETE_CATEGORY,
    ERROR_DUPLICATE_NAME,
    ERROR_EMPTY_NAME,
    SUCCESS_DELETE_CATEGORY,
    SUCCESS_UPDATE_CATEGORY,
    UPDATE_CATEGORY,
    VERIFY_DELETE_CAT,
    VERIFY_NAME,
    VERIFY_UPDATE_CAT,
    buttons,
)
from common.exceptions import Conflict, UpdateDatabaseError
from db import db_manager
from handlers.v1.admin.admin import cancel_keyboard
from models.models import CategoriesOrm
from services.base import BaseService, MixinStates


class MixinCategoryStates(MixinStates):
    selecting_category = State()


class AddCategoryStates(StatesGroup):
    waiting_for_name = State()


class EditCategoryStates(MixinCategoryStates):
    entering_new_name = State()


class DeleteCategoryStates(MixinCategoryStates):
    pass


def get_confirm_keyboard(confirm):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=buttons.confirm, callback_data=confirm)],
            [InlineKeyboardButton(text=buttons.cancel, callback_data="cancel")],
        ]
    )


class CategoriesService(BaseService):
    async def delete_category(self, callback: CallbackQuery, state: FSMContext):
        keyboard = await self._get_records_in_keyboard(callback, "delete_select_category_", "name")

        await callback.message.answer(DELETE_CATEGORY, reply_markup=keyboard)
        await callback.answer()

    async def update_category(self, callback: CallbackQuery, state: FSMContext):
        keyboard = await self._get_records_in_keyboard(callback, "select_category_", "name")

        await callback.message.answer(UPDATE_CATEGORY, reply_markup=keyboard)
        await callback.answer()

    async def select_category_for_delete(self, callback: CallbackQuery, state: FSMContext):
        category = await self._save_record_in_state(callback, state, "selected_category")
        if not category:
            return
        await callback.message.answer(
            VERIFY_DELETE_CAT % category.name,
            reply_markup=get_confirm_keyboard("confirm_delete"),
        )
        await state.set_state(DeleteCategoryStates.confirming)
        await callback.message.delete()

    async def select_category_for_update(self, callback: CallbackQuery, state: FSMContext):
        category = await self._save_record_in_state(callback, state, "selected_category")
        if not category:
            return

        await callback.message.answer(VERIFY_NAME % category.name, reply_markup=cancel_keyboard)
        await state.set_state(EditCategoryStates.entering_new_name)
        await callback.answer()
        await callback.message.delete()

    async def enter_new_name(self, message: types.Message, state: FSMContext):
        new_name = message.text.strip()
        if not new_name:
            await message.answer(ERROR_EMPTY_NAME, reply_markup=cancel_keyboard)
            await state.set_state(EditCategoryStates.entering_new_name)

            return

        await state.update_data(new_name=new_name)

        await message.answer(
            VERIFY_UPDATE_CAT % new_name,
            reply_markup=get_confirm_keyboard("confirm_edit"),
        )
        await state.set_state(EditCategoryStates.confirming)
        await message.delete()

    async def confirmation_delete(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        category_id = data["selected_category"]
        await self.table.delete_by_id(db_manager=self.db_manager, record_id=int(category_id))
        await callback.message.answer(SUCCESS_DELETE_CATEGORY)
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
            await callback.message.answer(SUCCESS_UPDATE_CATEGORY % new_category.name)
        except Conflict as e:
            await callback.message.answer(f"Ошибка: {e.args[0]}. Попробуйте другое имя.")
        except UpdateDatabaseError:
            await callback.message.answer(ERROR_DUPLICATE_NAME)
            await state.set_state(EditCategoryStates.entering_new_name)
            await callback.answer()
            return
        except Exception as e:
            await callback.message.answer(f"Неизвестная ошибка: {e}. Попробуйте позже.")

        await state.clear()
        await callback.answer()
        await callback.message.delete()


categories_tg_service = CategoriesService(db_manager, CategoriesOrm)
