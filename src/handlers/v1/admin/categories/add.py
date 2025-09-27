from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from buttons.buttons import ANSWER_ADD_CATEGORY, NAME_ADD_CATEGORY
from common.exceptions import Conflict
from handlers.v1.admin.admin import cancel_keyboard
from services.categories import AddProductStates, categories_tg_service

router = Router()


@router.callback_query(F.data == "add_category")
async def add_category(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(NAME_ADD_CATEGORY, reply_markup=cancel_keyboard)
    await state.set_state(AddProductStates.waiting_for_name)

    await callback.answer()


@router.message(AddProductStates.waiting_for_name)
async def add_name_category(message: types.Message, state: FSMContext):
    try:
        name = message.text.strip()
        new_catalog = await categories_tg_service.add(name)
        await message.answer(ANSWER_ADD_CATEGORY % new_catalog.name)
        await state.clear()
    except Conflict as e:
        await message.answer(e.args[0])
        await state.clear()
    except Exception as e:
        await message.answer(f"Ошибка: {e}. Попробуйте снова.")
        await state.clear()
