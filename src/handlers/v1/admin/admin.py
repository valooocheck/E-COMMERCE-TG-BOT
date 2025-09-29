from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from buttons.buttons import ANSWER_ADMIN, ANSWER_CANCEL, buttons
from common.decorators import db_interaction

router = Router()


cancel_keyboard = types.InlineKeyboardMarkup(
    inline_keyboard=[[types.InlineKeyboardButton(text=buttons.cancel, callback_data="cancel")]]
)


@router.message(Command("admin"))
@db_interaction.check_admin
async def admin(message: types.Message):
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(text=buttons.add_category, callback_data="add_category"))
    builder.row(types.InlineKeyboardButton(text=buttons.update_category, callback_data="update_category"))
    builder.row(types.InlineKeyboardButton(text=buttons.delete_category, callback_data="delete_category"))
    builder.row(types.InlineKeyboardButton(text=buttons.add_product, callback_data="add_product"))
    builder.row(types.InlineKeyboardButton(text=buttons.update_product, callback_data="update_product"))
    builder.row(types.InlineKeyboardButton(text=buttons.delete_product, callback_data="delete_product"))
    builder.row(types.InlineKeyboardButton(text=buttons.add_admin, callback_data="add_admin"))

    await message.answer(ANSWER_ADMIN, reply_markup=builder.as_markup())


@router.callback_query(F.data == "cancel")
async def cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(ANSWER_CANCEL)
    await callback.answer()
