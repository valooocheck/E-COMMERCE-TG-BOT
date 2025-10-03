from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from buttons.buttons import (
    ADDRESS_NOT_FOUND,
    ENTER_ADDRESS,
    NO_ADDRESS,
    NO_ORDERS_MESSAGE,
    SELECT_ADDRESS,
    SUCCESS_ADD_ADDRESS,
    buttons,
)
from common.exceptions import ClientNotFound, Conflict
from core.logger import log
from db import db_manager
from models.models import AddressesOrm, CartOrm, OrderItemsOrm, OrdersOrm, UsersOrm
from services.admin import cancel_keyboard
from services.base import BaseService


class OrderStates(StatesGroup):
    waiting_for_address_selection = State()
    adding_address = State()


class OrdersService(BaseService):
    async def create_order_from_cart(self, tg_id: int, address_id: int) -> OrdersOrm:
        async with self.db_manager.session() as session:
            try:
                user_query = select(UsersOrm).where(UsersOrm.tg_id == tg_id)
                user_result = await session.execute(user_query)
                user = user_result.scalar_one_or_none()
                if not user:
                    raise ClientNotFound(f"User with tg_id {tg_id} not found.")

                # Получаем товары из корзины
                cart_query = select(CartOrm).where(CartOrm.tg_id == tg_id)
                cart_result = await session.execute(cart_query)
                cart_items = cart_result.scalars().all()

                if not cart_items:
                    raise Conflict("Cart is empty. Cannot create order.")

                # Создаем новый заказ
                new_order = OrdersOrm(tg_id=tg_id, status="pending", address_id=address_id)  # Статус по умолчанию
                session.add(new_order)
                await session.flush()  # Получаем ID заказа

                # Добавляем позиции заказа из корзины
                for cart_item in cart_items:
                    order_item = OrderItemsOrm(
                        order_id=new_order.id, product_id=cart_item.product_id, quantity=cart_item.quantity
                    )
                    session.add(order_item)

                await session.execute(CartOrm.__table__.delete().where(CartOrm.tg_id == tg_id))

                await session.commit()
                log.info(f"Order {new_order.id} created from cart for user {tg_id}.")
                return new_order

            except IntegrityError as ex:
                await session.rollback()
                log.error("create_order_from_cart", ex)
                raise Conflict(f"Failed to create order: {ex}. Check for constraint violations.") from ex

    # async def place_order(self, callback: types.CallbackQuery, state: FSMContext):
    #     await admin_service.table.create_order_from_cart(self.db_manager, callback.from_user.id)
    async def get_user_addresses(self, tg_id):
        async with self.db_manager.session() as session:
            query = select(AddressesOrm).where(AddressesOrm.tg_id == tg_id)
            result = await session.execute(query)
            return result.scalars().all()

    async def place_order(self, callback: types.CallbackQuery, state: FSMContext):
        user_addresses = await self.get_user_addresses(callback.from_user.id)

        if not user_addresses:
            await callback.message.edit_text(NO_ADDRESS, reply_markup=cancel_keyboard)
            await state.set_state(OrderStates.adding_address)
        else:
            # Если адреса есть, показываем их для выбора
            await self.show_address_selection(callback.message, user_addresses, state)

    async def adding_address(self, message: types.Message, state: FSMContext):
        tg_id = message.from_user.id
        address_text = message.text

        async with self.db_manager.session() as session:
            new_address = AddressesOrm(tg_id=tg_id, address=address_text)
            session.add(new_address)
            await session.commit()

        await message.reply(SUCCESS_ADD_ADDRESS)

        user_addresses = await self.get_user_addresses(tg_id)
        await self.show_address_selection(message, user_addresses, state)

    async def show_address_selection(self, message, addresses, state):
        if not addresses:
            await message.answer(ADDRESS_NOT_FOUND)
            return

        keyboard = []
        for addr in addresses:
            keyboard.append([types.InlineKeyboardButton(text=addr.address, callback_data=f"select_address:{addr.id}")])

        keyboard.append([types.InlineKeyboardButton(text=buttons.add_address, callback_data="add_new_address")])

        markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(SELECT_ADDRESS, reply_markup=markup)
        await message.delete()

    # Предполагаем, что у вас есть сессия
    async def get_full_order(self, order_id: int):
        async with self.db_manager.session() as session:
            order = await session.scalar(
                select(OrdersOrm)
                .options(
                    selectinload(OrdersOrm.address),
                    selectinload(OrdersOrm.items).selectinload(OrderItemsOrm.product),
                    selectinload(OrdersOrm.user),
                )
                .where(OrdersOrm.id == order_id)
            )
            return order

    async def select_address(self, callback: types.CallbackQuery, state: FSMContext):
        address_id = int(callback.data.split(":")[-1])

        new_order = await self.create_order_from_cart(callback.from_user.id, address_id)
        new_order = await self.get_full_order(new_order.id)
        order_info = "🎉 Заказ успешно оформлен!\n\n"
        order_info += f"📋 Номер заказа: #{new_order.id}\n"
        order_info += f"📍 Адрес доставки: {new_order.address.address}\n\n"  # Предполагаем, что address загружен
        order_info += "🛒 Товары в заказе:\n"

        total_price = 0
        for item in new_order.items:  # Предполагаем, что order_items загружены
            product = item.product  # Предполагаем, что продукт загружен
            subtotal = item.quantity * product.price
            total_price += subtotal
            order_info += f"• {product.name} (x{item.quantity}) - {subtotal} ₽\n"

        order_info += f"\n💰 Итого: {total_price} ₽\n\n"
        order_info += "Спасибо за покупку! Мы скоро свяжемся с вами по поводу доставки. 🚚"

        await callback.message.edit_text(order_info, reply_markup=None)

        await state.clear()

    async def add_new_address(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(ENTER_ADDRESS, reply_markup=cancel_keyboard)
        await state.set_state(OrderStates.adding_address)

    async def get_user_orders(self, user_id: int):
        async with self.db_manager.session() as session:
            orders = await session.scalars(
                select(OrdersOrm)
                .where(OrdersOrm.tg_id == user_id)
                .options(
                    selectinload(OrdersOrm.user),
                    selectinload(OrdersOrm.address),
                    selectinload(OrdersOrm.items).selectinload(OrderItemsOrm.product),
                )
                .order_by(OrdersOrm.created_at.desc())
            )
            return orders.all()

    async def show_orders(self, callback: types.CallbackQuery, state: FSMContext):
        user_id = callback.from_user.id  # Получаем ID пользователя из Telegram

        orders = await self.get_user_orders(user_id)

        if not orders:
            await callback.message.edit_text(NO_ORDERS_MESSAGE)
            await callback.answer()
            return

        text = "*Ваши заказы:*\n\n"

        for order in orders:
            order_date = order.created_at.strftime("%d.%m.%Y %H:%M") if order.created_at else "Неизвестно"
            total = sum(item.product.price * item.quantity for item in order.items) if order.items else 0
            text += f"🛒 Заказ #{order.id}\n📅 {order_date}\n💰 Сумма: {total:.2f} руб.\n📊 Статус: {order.status}\n\n"

        await callback.message.edit_text(text, parse_mode="Markdown")
        await callback.answer()


orders_tg_service = OrdersService(db_manager, CartOrm)
