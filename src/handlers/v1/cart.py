from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from services.cart import cart_tg_service

router = Router()


@router.callback_query(F.data.startswith("add_basket_"))
async def add_basket(callback: types.CallbackQuery, state: FSMContext):
    await cart_tg_service.add_basket(callback, state)


@router.callback_query(F.data == "show_cart")
async def show_cart(callback: types.CallbackQuery, state: FSMContext):
    await cart_tg_service.show_cart(callback, state)


@router.callback_query(F.data == "delete_item_cart")
async def delete_item_cart(callback: types.CallbackQuery, state: FSMContext):
    await cart_tg_service.delete_item_cart(callback, state)


@router.callback_query(F.data.startswith("delete_item:"))
async def add_basket(callback: types.CallbackQuery, state: FSMContext):
    await cart_tg_service.delete_item(callback, state)
