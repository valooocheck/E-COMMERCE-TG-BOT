from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from common.decorators import db_interaction
from services.categories import DeleteCategoryStates, categories_tg_service

router = Router()


@router.callback_query(F.data == "delete_category")
@db_interaction.check_admin
async def delete_category(callback: types.CallbackQuery, state: FSMContext):
    await categories_tg_service.delete_category(callback, state)


@router.callback_query(F.data.startswith("delete_select_category_"))
@db_interaction.check_admin
async def select_category(callback: types.CallbackQuery, state: FSMContext):
    await categories_tg_service.select_category_for_delete(callback, state)


@router.callback_query(F.data == "confirm_delete", DeleteCategoryStates.confirming)
@db_interaction.check_admin
async def confirm_delete(callback: types.CallbackQuery, state: FSMContext):
    await categories_tg_service.confirmation_delete(callback, state)
