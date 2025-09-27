from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from services.categories import EditCategoryStates, categories_tg_service

router = Router()


@router.callback_query(F.data == "update_category")
async def update_category(callback: types.CallbackQuery, state: FSMContext):
    await categories_tg_service.update_category(callback, state)


@router.callback_query(F.data.startswith("select_category_"))
async def select_category(callback: types.CallbackQuery, state: FSMContext):
    await categories_tg_service.select_category_for_update(callback, state)


@router.message(EditCategoryStates.entering_new_name)
async def enter_new_name(message: types.Message, state: FSMContext):
    await categories_tg_service.enter_new_name(message, state)


@router.callback_query(F.data == "confirm_edit", EditCategoryStates.confirming)
async def confirm_edit(callback: types.CallbackQuery, state: FSMContext):
    await categories_tg_service.confirmation_changes(callback, state)
