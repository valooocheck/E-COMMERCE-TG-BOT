from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from services.products import UpdateProductStates, products_tg_service

router = Router()


@router.callback_query(F.data == "update_product")
async def update_product(callback: types.CallbackQuery):
    await products_tg_service.update_product(callback)


@router.callback_query(F.data.startswith("update_select_product_in_category_"))
async def select_category(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.select_category_for_update_product(callback, state)


@router.callback_query(F.data.startswith("select_product_in_category_update_"))
async def select_product_for_update(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.select_product_for_update(callback, state)


@router.callback_query(F.data.startswith("product_attr_name_for_update_"))
async def product_attr_name_for_update(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.product_attr_name_for_update(callback, state)


@router.message(UpdateProductStates.value)
async def update_attr(message: types.Message, state: FSMContext):
    await products_tg_service.update_attr(message, state)


@router.callback_query(F.data == "confirm_update_product")
async def confirm_delete(callback: types.CallbackQuery, state: FSMContext):
    # await products_tg_service.confirmation_delete_product(callback, state)
    await callback.message.answer("Подтверждение получено")
