from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from common.decorators import db_interaction
from services.categories import EditCategoryStates, categories_tg_service

router = Router()


@router.callback_query(F.data == "update_category")
@db_interaction.check_admin
async def update_category(callback: types.CallbackQuery, state: FSMContext):
    await categories_tg_service.update_category(callback, state)


@router.callback_query(F.data.startswith("select_category_"))
@db_interaction.check_admin
async def select_category(callback: types.CallbackQuery, state: FSMContext):
    await categories_tg_service.select_category_for_update(callback, state)


@router.message(EditCategoryStates.entering_new_name)
@db_interaction.check_admin
async def enter_new_name(message: types.Message, state: FSMContext):
    await categories_tg_service.enter_new_name(message, state)


@router.callback_query(F.data == "confirm_edit", EditCategoryStates.confirming)
@db_interaction.check_admin
async def confirm_edit(callback: types.CallbackQuery, state: FSMContext):
    await categories_tg_service.confirmation_changes(callback, state)
