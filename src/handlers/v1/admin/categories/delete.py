from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from services.categories import DeleteCategoryStates, categories_tg_service

router = Router()


@router.callback_query(F.data == "delete_category")
async def update_category(callback: types.CallbackQuery, state: FSMContext):
    await categories_tg_service.delete_category(callback, state)


@router.callback_query(F.data.startswith("delete_select_category_"))
async def select_category(callback: types.CallbackQuery, state: FSMContext):
    await categories_tg_service.select_category_for_delete(callback, state)


@router.callback_query(F.data == "confirm_delete", DeleteCategoryStates.confirming)
async def confirm_delete(callback: types.CallbackQuery, state: FSMContext):
    await categories_tg_service.confirmation_delete(callback, state)
