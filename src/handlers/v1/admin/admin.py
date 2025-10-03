from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from buttons.buttons import ANSWER_ADMIN, ANSWER_CANCEL, buttons
from common.decorators import db_interaction
from services.admin import AddAdminStates, UpdateStatusOrdersStates, admin_service

router = Router()


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
    builder.row(types.InlineKeyboardButton(text=buttons.viewing_orders, callback_data="viewing_orders"))

    await message.answer(ANSWER_ADMIN, reply_markup=builder.as_markup())


@router.callback_query(F.data == "add_admin")
@db_interaction.check_admin
async def add_admin(callback: types.CallbackQuery, state: FSMContext):
    await admin_service.add_admin(callback, state)


@router.callback_query(F.data.startswith("admin_order_manage:"))
@db_interaction.check_admin
async def select_category_show_product(callback: types.CallbackQuery, state: FSMContext):
    await admin_service.order_manage(callback, state)


@router.message(UpdateStatusOrdersStates.status)
@db_interaction.check_admin
async def update_status(message: types.Message, state: FSMContext):
    await admin_service.update_status(message, state)


@router.callback_query(F.data == "viewing_orders")
@db_interaction.check_admin
async def viewing_orders(callback: types.CallbackQuery, state: FSMContext):
    await admin_service.viewing_orders(callback, state)


@router.callback_query(F.data == "add_admin")
@db_interaction.check_admin
async def add_admin(callback: types.CallbackQuery, state: FSMContext):
    await admin_service.add_admin(callback, state)


@router.message(AddAdminStates.name)
@db_interaction.check_admin
async def add_admin_name(message: types.Message, state: FSMContext):
    await admin_service.add_admin_name(message, state)


@router.callback_query(F.data == "cancel")
async def cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(ANSWER_CANCEL)
    await callback.answer()
