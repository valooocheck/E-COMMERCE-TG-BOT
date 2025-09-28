from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from buttons.buttons import DESCRIPTION_ADD_PRODUCT, NAME_ADD_PRODUCT
from handlers.v1.admin.admin import cancel_keyboard
from services.products import AddProductStates, products_tg_service

router = Router()


@router.callback_query(F.data == "add_product")
async def add_product(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(NAME_ADD_PRODUCT, reply_markup=cancel_keyboard)
    await state.set_state(AddProductStates.name)

    await callback.answer()


@router.message(AddProductStates.name)
async def add_name_product(message: types.Message, state: FSMContext):
    try:
        if name := message.text.strip():
            await state.update_data(name=name.lower())
            await message.answer(DESCRIPTION_ADD_PRODUCT, reply_markup=cancel_keyboard)
            await state.set_state(AddProductStates.description)
    except Exception as e:
        await message.answer(e)


@router.message(AddProductStates.description)
async def add_description_product(message: types.Message, state: FSMContext):
    try:
        if description := message.text.strip():
            await state.update_data(description=description)
            await products_tg_service.choice_category(message, state)
    except Exception as e:
        await message.answer(e)


@router.callback_query(F.data.startswith("category_for_add_product_"))
async def select_category(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.select_category_for_add_product(callback, state)


@router.message(AddProductStates.price)
async def add_price_product(message: types.Message, state: FSMContext):
    await products_tg_service.add_price_product(message, state)


@router.message(AddProductStates.photo)
async def add_photo_product(message: types.Message, state: FSMContext):
    await products_tg_service.add_photo_product(message, state)


@router.callback_query(F.data == "confirm_add_product", AddProductStates.confirming)
async def confirm_edit(callback: types.CallbackQuery, state: FSMContext):
    await products_tg_service.confirm_add_product(callback, state)
