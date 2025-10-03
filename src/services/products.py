from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select

from buttons.buttons import (
    ANSWER_ADMIN_ERROR_PRICE,
    ANSWER_FOR_UPDATE_ATTR,
    ANSWER_NOT_PRODUCT,
    CARD_TEMPLATE,
    CATEGORY_CHOOSE,
    CATEGORY_FOR_PRODUCT,
    CHOOSE_CATEGORY_DELETE_PRODUCT,
    CHOOSE_CATEGORY_FOR_UPDATE_PRODUCT,
    CHOOSE_CATEGORY_UPDATE_PRODUCT,
    CHOOSE_DELETE_PRODUCT,
    CHOOSE_PRODUCT,
    CHOOSE_UPDATE_PRODUCT,
    CHOOSE_UPDATE_PRODUCT_ATTRIBUTE,
    ERROR_UPDATE_ATTR,
    PHOTO_FOR_PRODUCT,
    PHOTO_NOT_FOR_PRODUCT,
    PRICE_FOR_PRODUCT,
    SUCCESS_ADD_PRODUCT,
    SUCCESS_DELETE_PRODUCT,
    SUCCESS_UPDATE_PRODUCT,
    UPDATE_PHOTO,
    VERIFY_ADD_PRODUCT,
    VERIFY_DELETE_PRODUCT,
    VERIFY_UPDATE_CAT,
    VERIFY_UPDATE_CAT_IN_PROD,
    VERIFY_UPDATE_PHOTO,
    buttons,
)
from db import db_manager
from models.models import CategoriesOrm, ProductsOrm
from services.admin import cancel_keyboard
from services.base import BaseService, MixinStates
from services.categories import categories_tg_service, get_confirm_keyboard


class AddProductStates(MixinStates):
    name = State()
    description = State()
    price = State()
    photo = State()
    category_id = State()
    quantity = State()


class UpdateProductStates(MixinStates):
    value = State()


class ProductsService(BaseService):
    @staticmethod
    async def choice_category(message: types.CallbackQuery, state: FSMContext):
        keyboard = await categories_tg_service._get_records_in_keyboard(message, "category_for_add_product_", "name")
        if keyboard:
            await message.answer(CATEGORY_FOR_PRODUCT, reply_markup=keyboard)

    @staticmethod
    async def select_category_for_add_product(callback: types.CallbackQuery, state: FSMContext):
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

    @staticmethod
    async def add_price_product(message: types.Message, state: FSMContext):
        try:
            if price := int(message.text.strip()):
                await state.update_data(price=price)
                await message.answer(PHOTO_FOR_PRODUCT, reply_markup=cancel_keyboard)
                await state.set_state(AddProductStates.photo)
        except Exception:
            await message.answer(ANSWER_ADMIN_ERROR_PRICE, reply_markup=cancel_keyboard)
            await state.set_state(AddProductStates.price)
            return

    @staticmethod
    async def gen_product_card(name: str, description: str, price: int, category_id: int, quantity: int):
        category = await categories_tg_service._get_by_id(category_id)
        # return f"Название товара: {name} \nЦена: {price}₽ \nОписание: {description}\nКатегория: {category.name}\nКоличество: {quantity}"
        return CARD_TEMPLATE % (str(name), str(price), str(description), str(category.name), str(quantity))

    async def confirmation_add(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        category_id = data.get("category_id")
        name = data.get("name")
        description = data.get("description")
        price = data.get("price")
        photo_bytes = data.get("photo")
        quantity = data.get("quantity")

        card_prod = await self.gen_product_card(name, description, price, category_id, quantity)

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
            name=data.get("name"), description=data.get("description"), price=data.get("price"), photo=data.get("photo")
        )
        product.category = await categories_tg_service._get_by_id(data.get("category_id"))
        await product.save(self.db_manager)

    async def confirm_add_product(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await self._add_product(state)
        await callback.message.answer(SUCCESS_ADD_PRODUCT)

        await state.clear()

    @staticmethod
    async def delete_product(callback: CallbackQuery):
        keyboard = await categories_tg_service._get_records_in_keyboard(
            callback, "delete_select_product_in_category_", "name"
        )
        await callback.message.answer(CHOOSE_CATEGORY_DELETE_PRODUCT, reply_markup=keyboard)

    @staticmethod
    async def update_product(callback: CallbackQuery):
        keyboard = await categories_tg_service._get_records_in_keyboard(
            callback, "update_select_product_in_category_", "name"
        )
        await callback.message.answer(CHOOSE_CATEGORY_UPDATE_PRODUCT, reply_markup=keyboard)

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

    async def select_category_for_update_product(self, callback: CallbackQuery, state: FSMContext):
        category = await categories_tg_service._save_record_in_state(callback, state, "category_id")
        if not category:
            return
        where_conditions = [self.table.category_id == category.id]
        keyboard = await self._get_records_in_keyboard(
            callback, "select_product_in_category_update_", "name", where_conditions
        )
        if keyboard:
            await callback.message.answer(
                CHOOSE_UPDATE_PRODUCT,
                reply_markup=keyboard,
            )
            await callback.message.delete()

    async def select_product_for_delete(self, callback: CallbackQuery, state: FSMContext):
        product = await self._save_record_in_state(callback, state, "product_id")
        if not product:
            return
        card = await self.gen_product_card(
            product.name, product.description, product.price, product.category_id, product.quantity
        )
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

    async def select_product_for_update(self, callback: CallbackQuery, state: FSMContext):
        product = await self._save_record_in_state(callback, state, "product_id")
        if not product:
            return
        card = await self.gen_product_card(
            product.name, product.description, product.price, product.category_id, product.quantity
        )
        photo_file = BufferedInputFile(product.photo, filename="product.jpg")

        await callback.message.answer_photo(
            photo=photo_file,
            caption=card,
            parse_mode="HTML",
        )
        column_names = {
            "name": "Имя товара",
            "description": "Описание",
            "price": "цена",
            "photo": "фото",
            "quantity": "Количество",
            "category": "Категория",
        }

        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        for k, v in column_names.items():
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=v,
                        callback_data="product_attr_name_for_update_" + k,
                    )
                ]
            )
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=buttons.cancel, callback_data="cancel")])

        await callback.message.answer(
            CHOOSE_UPDATE_PRODUCT_ATTRIBUTE,
            reply_markup=keyboard,
        )
        await callback.message.delete()

    async def product_attr_name_for_update(self, callback: types.CallbackQuery, state: FSMContext):
        name_attr = callback.data.split("_")[-1]
        await state.update_data({"name_attr": name_attr})
        data = await state.get_data()
        product = await self.table.find_by_id(self.db_manager, int(data["product_id"]))
        if name_attr == "category":
            keyboard = await categories_tg_service._get_records_in_keyboard(
                callback, "category_in_product_for_update_", "name"
            )
            if keyboard:
                await callback.message.answer(
                    CHOOSE_CATEGORY_FOR_UPDATE_PRODUCT,
                    reply_markup=keyboard,
                )
                await callback.message.delete()
                return
        elif name_attr in ["name", "description", "price", "quantity"]:
            await callback.message.answer(
                ANSWER_FOR_UPDATE_ATTR % str(getattr(product, name_attr)), reply_markup=cancel_keyboard
            )
        elif name_attr == "photo":
            await callback.message.answer(UPDATE_PHOTO, reply_markup=cancel_keyboard)
        await callback.message.delete()
        await state.set_state(UpdateProductStates.value)

    async def update_photo_product(self, message: types.Message, state: FSMContext):
        if not message.photo:
            await message.answer(PHOTO_NOT_FOR_PRODUCT, reply_markup=cancel_keyboard)
            await state.set_state(UpdateProductStates.value)
            return

        photo = await self._download_photo(message)

        await state.update_data(value=photo.read())

    async def update_attr(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        if data["name_attr"] == "category":
            pass
        elif data["name_attr"] in ["name", "description", "price", "quantity"]:
            value = message.text.strip()
            if not value:
                await message.answer(ERROR_UPDATE_ATTR, reply_markup=cancel_keyboard)
                await state.set_state(UpdateProductStates.value)
                return

            await state.update_data(value=value)
            await message.answer(
                VERIFY_UPDATE_CAT % value,
                reply_markup=get_confirm_keyboard("confirm_update_product"),
            )
        elif data["name_attr"] == "photo":
            await self.update_photo_product(message, state)
            await message.answer(
                VERIFY_UPDATE_PHOTO,
                reply_markup=get_confirm_keyboard("confirm_update_product"),
            )
        await state.set_state(UpdateProductStates.confirming)

    async def confirmation_delete_product(self, callback: CallbackQuery, state: FSMContext):
        await callback.message.delete()
        data = await state.get_data()
        await self.table.delete_by_id(self.db_manager, int(data.get("product_id")))
        await callback.message.answer(SUCCESS_DELETE_PRODUCT)

        await state.clear()

    async def select_category_in_product_for_update(self, callback: types.CallbackQuery, state: FSMContext):
        cat = await categories_tg_service._save_record_in_state(callback, state, "value")
        await callback.message.answer(
            VERIFY_UPDATE_CAT_IN_PROD % cat.name,
            reply_markup=get_confirm_keyboard("confirm_update_product"),
        )
        await state.set_state(UpdateProductStates.confirming)

    async def _update_product(self, state: FSMContext):
        data = await state.get_data()
        if data["name_attr"] == "category":
            async with db_manager.session() as session:
                query = select(CategoriesOrm).where(CategoriesOrm.id == int(data.get("value")))
                result = await session.execute(query)
                category = result.scalar_one_or_none()

                query = select(ProductsOrm).where(ProductsOrm.id == int(data.get("product_id")))
                result = await session.execute(query)
                result = result.scalar_one_or_none()
                result.category = category
                await session.commit()
                return result
        elif data["name_attr"] == "price":
            data["value"] = int(data["value"])
        elif data["name_attr"] == "quantity":
            data["value"] = int(data["value"])
        product = await self.table.update_by_id(
            db_manager=self.db_manager,
            record_id=int(data.get("product_id")),
            **{data.get("name_attr"): data.get("value")},
        )

        return product

    async def confirmation_update(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.delete()
        await self._update_product(state)
        await callback.message.answer(SUCCESS_UPDATE_PRODUCT)

        await state.clear()

    @staticmethod
    async def show_catalog(callback: types.CallbackQuery):
        keyboard = await categories_tg_service._get_records_in_keyboard(callback, "catalog_categories_", "name")
        if keyboard:
            await callback.message.answer(CATEGORY_CHOOSE, reply_markup=keyboard)
            await callback.answer()

    async def select_category_show_product(self, callback: types.CallbackQuery, state: FSMContext):
        cat_id = callback.data.split("_")[-1]

        keyboard = await self._get_records_in_keyboard(
            callback, "catalog_product_", "name", [self.table.category_id == int(cat_id)]
        )
        await callback.message.answer(
            CHOOSE_PRODUCT,
            reply_markup=keyboard,
        )
        await callback.answer()

    async def catalog_product(self, callback: types.CallbackQuery, state: FSMContext):
        prod_id = callback.data.split("_")[-1]
        product = await self.table.find_by_id(db_manager=self.db_manager, record_id=int(prod_id))
        if not product:
            await callback.message.answer(ANSWER_NOT_PRODUCT)
            return await callback.answer()
        card = await self.gen_product_card(
            product.name, product.description, product.price, product.category_id, product.quantity
        )
        photo_file = BufferedInputFile(product.photo, filename="product.jpg")

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=buttons.next_product,
                        callback_data=f"catalog_product_{int(prod_id) + 1}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=buttons.previous_product,
                        callback_data=f"catalog_product_{int(prod_id) - 1}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=buttons.add_basket,
                        callback_data=f"add_basket_{int(prod_id)}",
                    )
                ],
            ]
        )

        await callback.message.answer_photo(
            photo=photo_file,
            caption=card,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
        await callback.answer()


products_tg_service = ProductsService(db_manager, ProductsOrm)
