from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from buttons.buttons import ANSWER_CONFLICT_ADD, RECORD_NOT_FOUND, RECORDS_NOT_FOUND, buttons
from common.exceptions import Conflict
from db.session_manager import DatabaseSessionManager


class MixinStates(StatesGroup):
    confirming = State()


class BaseService:
    def __init__(self, db_man: DatabaseSessionManager, table) -> None:
        self.db_manager = db_man
        self.table = table

    async def _download_photo(self, message: types.Message):
        try:
            photo = message.photo[-1]
            file_info = await message.bot.get_file(photo.file_id)
            downloaded_file = await message.bot.download_file(file_info.file_path)

            return downloaded_file

        except Exception as e:
            await message.answer(f"Ошибка при сохранении фото: {e}")

    async def _get_by_id(self, id: int):
        return await self.table.find_by_id(self.db_manager, id)

    async def add(self, data):
        new_record = self.table(name=data)
        try:
            await new_record.save(self.db_manager)
        except Conflict:
            raise Conflict(ANSWER_CONFLICT_ADD % data) from None
        return new_record

    async def _get_all(self, where_conditions=None):
        if where_conditions:
            where_conditions = list(where_conditions)
        return await self.table.find_all(db_manager=self.db_manager, where_conditions=where_conditions)

    async def _get_records_in_keyboard(
        self, callback: types.CallbackQuery | types.Message, callback_data: str, name_attr: str, conditions=None
    ):
        records = await self._get_all(where_conditions=conditions)

        if not records:
            if isinstance(callback, types.Message):
                await callback.answer(RECORD_NOT_FOUND)
                return
            await callback.message.answer(RECORDS_NOT_FOUND)
            await callback.answer()
            return

        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        for record in records:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=getattr(record, name_attr),
                        callback_data=f"{callback_data}{record.id}",
                    )
                ]
            )

        keyboard.inline_keyboard.append([InlineKeyboardButton(text=buttons.cancel, callback_data="cancel")])
        return keyboard

    async def _save_record_in_state(self, callback: CallbackQuery, state: FSMContext, name_state: str):
        record_id = callback.data.split("_")[-1]

        record = await self.table.find_by_id(self.db_manager, int(record_id))
        if not record:
            await callback.message.answer(RECORD_NOT_FOUND)
            await callback.answer()

        await state.update_data(**{name_state: record.id})
        return record
