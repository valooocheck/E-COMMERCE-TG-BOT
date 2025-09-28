from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import BufferedInputFile, CallbackQuery

from buttons.buttons import (
    CATEGORY_FOR_PRODUCT,
    CHOOSE_CATEGORY_DELETE_PRODUCT,
    CHOOSE_DELETE_PRODUCT,
    PHOTO_FOR_PRODUCT,
    PHOTO_NOT_FOR_PRODUCT,
    PRICE_FOR_PRODUCT,
    SUCCESS_ADD_PRODUCT,
    SUCCESS_DELETE_PRODUCT,
    VERIFY_ADD_PRODUCT,
    VERIFY_DELETE_PRODUCT,
)
from db import db_manager
from handlers.v1.admin.admin import cancel_keyboard
from models.models import ProductsOrm
from services.base import BaseService, MixinStates
from services.categories import categories_tg_service, get_confirm_keyboard


class AddProductStates(MixinStates):
    name = State()
    description = State()
    price = State()
    photo = State()
    category_id = State()
    quantity = State()


class ProductsService(BaseService):
    @staticmethod
    async def choice_category(message: types.CallbackQuery, state: FSMContext):
        keyboard = await categories_tg_service._get_records_in_keyboard(message, "category_for_add_product_", "name")

        await message.answer(CATEGORY_FOR_PRODUCT, reply_markup=keyboard)
        # await state.set_state(AddCategoryStates.waiting_for_name)

    async def select_category_for_add_product(self, callback: types.CallbackQuery, state: FSMContext):
        category = await categories_tg_service._save_record_in_state(callback, state, "category_id")
        if not category:
            return
        await callback.message.answer(PRICE_FOR_PRODUCT, reply_markup=cancel_keyboard)
        await state.set_state(AddProductStates.price)

    async def add_photo_product(self, message: types.Message, state: FSMContext):
        if not message.photo:
            await message.answer(PHOTO_NOT_FOR_PRODUCT, reply_markup=cancel_keyboard)
            await state.set_state(AddProductStates.photo)
            return

        photo = await self._download_photo(message)

        await state.update_data({"photo": photo.read()})

        await self.confirmation_add(message, state)

    async def add_price_product(self, message: types.Message, state: FSMContext):
        try:
            if price := float(message.text.strip()):
                await state.update_data(price=price)
                # await state.set_state(AddProductStates.confirming)
                await message.answer(PHOTO_FOR_PRODUCT, reply_markup=cancel_keyboard)
                await state.set_state(AddProductStates.photo)
        except Exception as e:
            await message.answer(e)
            return

    @staticmethod
    async def gen_product_card(name: str, description: str, price: float, category_id: int):
        category = await categories_tg_service._get_by_id(category_id)
        return f"Название товара: {name} \nЦена: {price}₽ \nОписание: {description}\nКатегория: {category.name}"

    async def confirmation_add(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        category_id = data.get("category_id")
        name = data.get("name")
        description = data.get("description")
        price = data.get("price")
        photo_bytes = data.get("photo")

        card_prod = await self.gen_product_card(name, description, price, category_id)

        photo_file = BufferedInputFile(photo_bytes, filename="product.jpg")

        await message.answer_photo(
            photo=photo_file,
            caption=card_prod,
            parse_mode="HTML",
        )

        await message.answer(
            VERIFY_ADD_PRODUCT,
            reply_markup=get_confirm_keyboard("confirm_add_product"),
        )
        await state.set_state(AddProductStates.confirming)
        await message.delete()

    async def _add_product(self, state: FSMContext):
        data = await state.get_data()
        product = self.table(
            name=data.get("name"),
            description=data.get("description"),
            price=data.get("price"),
            photo=data.get("photo"),
            quantity=52,
        )
        product.category = await categories_tg_service._get_by_id(data.get("category_id"))
        await product.save(self.db_manager)

    async def confirm_add_product(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await self._add_product(state)
        await callback.message.answer(SUCCESS_ADD_PRODUCT)

        await state.clear()

    async def delete_product(self, callback: CallbackQuery):
        keyboard = await categories_tg_service._get_records_in_keyboard(
            callback, "delete_select_product_in_category_", "name"
        )
        await callback.message.answer(CHOOSE_CATEGORY_DELETE_PRODUCT, reply_markup=keyboard)

    async def select_category_for_delete_product(self, callback: CallbackQuery, state: FSMContext):
        category = await self._save_record_in_state(callback, state, "category_id")
        if not category:
            return
        keyboard = await self._get_records_in_keyboard(
            callback, "select_product_in_category_delete_", "name", self.table.category_id == category.id
        )
        await callback.message.answer(
            CHOOSE_DELETE_PRODUCT,
            reply_markup=keyboard,
        )
        await callback.message.delete()

    async def select_product_for_delete(self, callback: CallbackQuery, state: FSMContext):
        product = await self._save_record_in_state(callback, state, "product_id")
        if not product:
            return
        card = await self.gen_product_card(product.name, product.description, product.price, product.category_id)
        photo_file = BufferedInputFile(product.photo, filename="product.jpg")

        await callback.message.answer_photo(
            photo=photo_file,
            caption=card,
            parse_mode="HTML",
        )

        await callback.message.answer(
            VERIFY_DELETE_PRODUCT,
            reply_markup=get_confirm_keyboard("confirm_delete_product"),
        )
        await callback.message.delete()

    async def confirmation_delete_product(self, callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        data = await state.get_data()
        await self.table.delete_by_id(self.db_manager, int(data.get("product_id")))
        await callback.message.answer(SUCCESS_DELETE_PRODUCT)

        await state.clear()


products_tg_service = ProductsService(db_manager, ProductsOrm)
