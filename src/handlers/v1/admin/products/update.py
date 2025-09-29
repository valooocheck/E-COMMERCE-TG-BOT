from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from common.decorators import db_interaction
from services.products import UpdateProductStates, products_tg_service

router = Router()


@router.callback_query(F.data == "update_product")
@db_interaction.check_admin
async def update_product(callback: types.CallbackQuery):
    await products_tg_service.update_product(callback)


@router.callback_query(F.data.startswith("update_select_product_in_category_"))
@db_interaction.check_admin
async def select_category(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.select_category_for_update_product(callback, state)


@router.callback_query(F.data.startswith("select_product_in_category_update_"))
@db_interaction.check_admin
async def select_product_for_update(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.select_product_for_update(callback, state)


@router.callback_query(F.data.startswith("product_attr_name_for_update_"))
@db_interaction.check_admin
async def product_attr_name_for_update(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.product_attr_name_for_update(callback, state)


@router.message(UpdateProductStates.value)
@db_interaction.check_admin
async def update_attr(message: types.Message, state: FSMContext):
    await products_tg_service.update_attr(message, state)


@router.callback_query(F.data.startswith("category_in_product_for_update_"))
@db_interaction.check_admin
async def product_attr_name_for_update(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.select_category_in_product_for_update(callback, state)


@router.callback_query(F.data == "confirm_update_product")
@db_interaction.check_admin
async def confirmation_update(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.confirmation_update(callback, state)
