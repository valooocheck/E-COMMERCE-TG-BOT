from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from services.products import products_tg_service

router = Router()


@router.callback_query(F.data == "delete_product")
async def delete_product(callback: types.CallbackQuery):
    await products_tg_service.delete_product(callback)


@router.callback_query(F.data.startswith("delete_select_product_in_category_"))
async def select_category(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.select_category_for_delete_product(callback, state)


@router.callback_query(F.data.startswith("select_product_in_category_delete_"))
async def select_product_for_delete(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.select_product_for_delete(callback, state)


@router.callback_query(
    F.data == "confirm_delete_product",
)
async def confirm_delete(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.confirmation_delete_product(callback, state)
