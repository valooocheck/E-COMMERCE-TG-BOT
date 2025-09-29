from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from buttons.buttons import ANSWER_NOT_FOUND_USER, NAME_USER_ADMIN_ADD, buttons
from common.exceptions import ClientNotFound, Conflict
from db import db_manager
from models.models import UsersOrm
from services.base import BaseService


class AddAdminStates(StatesGroup):
    name = State()


cancel_keyboard = types.InlineKeyboardMarkup(
    inline_keyboard=[[types.InlineKeyboardButton(text=buttons.cancel, callback_data="cancel")]]
)


class AdminService(BaseService):
    async def add_admin(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.answer(NAME_USER_ADMIN_ADD, reply_markup=cancel_keyboard)
        await state.set_state(AddAdminStates.name)
        await callback.message.delete()

    async def add_admin_name(self, message: types.Message, state: FSMContext):
        try:
            name = message.text.strip()
            if name.startswith("@"):
                name = name.strip("@")
            await self.table.update_by_tg_username(self.db_manager, name, **{"is_admin": True})
            await message.answer("Успех")
            await state.clear()
        except ClientNotFound:
            await state.clear()
            await message.answer(ANSWER_NOT_FOUND_USER, reply_markup=cancel_keyboard)
            await state.set_state(AddAdminStates.name)
        except Conflict as e:
            await message.answer(e.args[0])
            await state.clear()
        except Exception as e:
            await message.answer(f"Ошибка: {e}. Попробуйте снова.")
            await state.clear()


admin_service = AdminService(db_manager, UsersOrm)
