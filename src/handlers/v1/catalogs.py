from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from services.products import products_tg_service

router = Router()


@router.callback_query(F.data == "show_catalog")
async def show_catalog(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.show_catalog(callback)


@router.callback_query(F.data.startswith("catalog_categories_"))
async def select_category_show_product(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.select_category_show_product(callback, state)


@router.callback_query(F.data.startswith("catalog_product_"))
async def select_category(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.catalog_product(callback, state)
