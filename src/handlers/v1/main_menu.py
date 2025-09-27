from aiogram import Router, types
from aiogram.filters.command import Command

from common.decorators import db_interaction

router = Router()


@router.message(Command("start"))
@db_interaction.main_menu
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, @{message.from_user.username}! Выбери пункт из предложенного!",
    )
