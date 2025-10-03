from typing import Any

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from buttons.buttons import ANSWER_ADD_CART, EMPTY_CART, buttons
from db import db_manager
from models.models import CartOrm
from services.base import BaseService


class CartService(BaseService):
    async def add_product_to_cart(self, tg_id: int, product_id: int, quantity: int = 1):
        async with self.db_manager.session() as session:
            # Проверяем, есть ли уже такой товар в корзине пользователя
            query = select(self.table).where(self.table.tg_id == tg_id, self.table.product_id == product_id)
            result = await session.execute(query)
            cart_item = result.scalar_one_or_none()

            if cart_item:
                cart_item.quantity += quantity
                session.add(cart_item)
            else:
                cart_item = CartOrm(tg_id=tg_id, product_id=product_id, quantity=quantity)
                session.add(cart_item)

            try:
                await session.commit()
            except IntegrityError as ex:
                await session.rollback()
                # Логируйте или обрабатывайте ошибку по необходимости
                raise ex

            return cart_item

    async def add_basket(self, callback: types.CallbackQuery, state: FSMContext):
        product_id = int(callback.data.split("_")[-1])
        await self.add_product_to_cart(callback.from_user.id, product_id)
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text=buttons.show_cart, callback_data="show_cart"))
        await callback.message.answer(ANSWER_ADD_CART, reply_markup=builder.as_markup())
        await callback.answer()

    async def _get_cart_user(self, tg_id: int) -> Any:
        async with self.db_manager.session() as session:
            # Запрос корзины с загрузкой связанных продуктов
            query = select(CartOrm).where(CartOrm.tg_id == tg_id).options(selectinload(CartOrm.product))
            result = await session.execute(query)
            return result.scalars().all()

    async def get_cart(self, tg_id: int):
        cart_items = await self._get_cart_user(tg_id)

        # Формируем ответ
        items = []
        total_price = 0
        for item in cart_items:
            product = item.product
            item_total = product.price * item.quantity
            total_price += item_total
            items.append(
                {
                    "product_id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "quantity": item.quantity,
                    "item_total": item_total,
                }
            )

        return {"items": items, "total_price": total_price}

    async def show_cart(self, callback: types.CallbackQuery, state: FSMContext):
        cart_data = await self.get_cart(callback.from_user.id)
        if not cart_data["items"]:
            await callback.answer(EMPTY_CART)
            return await callback.message.answer(EMPTY_CART)

        text = "🛒 <b>Ваша корзина:</b>\n\n"
        for item in cart_data["items"]:
            name = item["name"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            description = item["description"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

            text += f"• <i>{name}</i>\n"
            text += f"  <i>{description}</i>\n"
            text += f"  Цена: {item['price']} ₽ | Кол-во: {item['quantity']} | Итого: {item['item_total']} ₽\n\n"

        text += f"💰 <b>Общая стоимость:</b> {cart_data['total_price']} ₽\n\n"

        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=buttons.place_order, callback_data="place_order")],
                    [InlineKeyboardButton(text=buttons.delete_item_cart, callback_data="delete_item_cart")],
                ]
            ),
        )
        await callback.answer()

    async def delete_item_cart(self, callback: types.CallbackQuery, state: FSMContext):
        cart_data = await self.get_cart(callback.from_user.id)
        if not cart_data["items"]:
            await callback.message.answer("🛒 Ваша корзина пуста.", parse_mode="HTML")
            await callback.answer()
            return
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for item in cart_data["items"]:
            button_text = f"🗑️ {item['name']}"
            callback_data = f"delete_item:{item['product_id']}"
            keyboard.inline_keyboard.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])

        await callback.message.answer(
            "🗑️ Выберите товар для удаления из корзины:", parse_mode="HTML", reply_markup=keyboard
        )
        await callback.answer()

    async def delete_cart_item(self, tg_id: int, item_id: int):
        async with self.db_manager.session() as session:
            stmt = delete(CartOrm).where(CartOrm.tg_id == tg_id, CartOrm.product_id == item_id)
            await session.execute(stmt)
            await session.commit()

    async def delete_item(self, callback: types.CallbackQuery, state: FSMContext):
        user_id = callback.from_user.id
        try:
            item_id = int(callback.data.split(":")[-1])
        except (IndexError, ValueError):
            await callback.message.answer("❌ Ошибка: некорректный запрос.")
            return await callback.answer()
        try:
            await self.delete_cart_item(user_id, item_id)

            cart_data = await self.get_cart(callback.from_user.id)

            if not cart_data["items"]:
                await callback.message.edit_text("✅ Товар удалён! 🛒 Ваша корзина пуста.", parse_mode="HTML")
                return await callback.answer("Товар удалён!")

            keyboard = InlineKeyboardMarkup(inline_keyboard=[])
            for item in cart_data["items"]:
                button_text = f"🗑️ {item['name']}"
                callback_data = f"delete_item:{item['product_id']}"
                keyboard.inline_keyboard.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])

            await callback.message.edit_text(
                "✅ Товар удалён! 🗑️ Выберите следующий товар для удаления:", parse_mode="HTML", reply_markup=keyboard
            )
            await callback.answer("Товар удалён!")

        except Exception as e:
            await callback.message.answer("❌ Ошибка при удалении товара. Попробуйте позже.")
            print(f"Ошибка удаления: {e}")

        await callback.answer()


cart_tg_service = CartService(db_manager, CartOrm)
