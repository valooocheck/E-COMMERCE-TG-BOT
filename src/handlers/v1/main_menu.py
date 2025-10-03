from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from buttons.buttons import HELLO_CLIENT, buttons
from common.decorators import db_interaction

router = Router()


@router.message(Command("start"))
@db_interaction
async def admin(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=buttons.show_catalog, callback_data="show_catalog"))
    builder.row(types.InlineKeyboardButton(text=buttons.show_cart, callback_data="show_cart"))
    builder.row(types.InlineKeyboardButton(text=buttons.show_orders, callback_data="show_orders"))
    await message.answer(HELLO_CLIENT % message.from_user.username, reply_markup=builder.as_markup())
