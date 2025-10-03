from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from services.orders import OrderStates, orders_tg_service

router = Router()


@router.callback_query(F.data == "show_orders")
async def show_orders(callback: types.CallbackQuery, state: FSMContext):
    await orders_tg_service.show_orders(callback, state)


@router.callback_query(F.data == "place_order")
async def place_order(callback: types.CallbackQuery, state: FSMContext):
    await orders_tg_service.place_order(callback, state)


@router.callback_query(F.data.startswith("select_address:"))
async def select_category_show_product(callback: types.CallbackQuery, state: FSMContext):
    await orders_tg_service.select_address(callback, state)


@router.callback_query(F.data == "add_new_address")
async def place_order(callback: types.CallbackQuery, state: FSMContext):
    await orders_tg_service.add_new_address(callback, state)


@router.message(OrderStates.adding_address)
async def adding_address(message: types.Message, state: FSMContext):
    await orders_tg_service.adding_address(message, state)
