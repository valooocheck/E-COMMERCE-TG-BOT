from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from buttons.buttons import (
    ANSWER_NOT_FOUND_USER,
    NAME_USER_ADMIN_ADD,
    ORDER_NOT_FOUND,
    ORDER_UPDATE_STATUS,
    SUCCESS_ADD_ADMIN,
    SUCCESS_UPDATE_STATUS,
    buttons,
)
from common.exceptions import ClientNotFound, Conflict
from db import db_manager
from models.models import OrderItemsOrm, OrdersOrm, UsersOrm
from services.base import BaseService


class AddAdminStates(StatesGroup):
    name = State()


class UpdateStatusOrdersStates(StatesGroup):
    status = State()


cancel_keyboard = types.InlineKeyboardMarkup(
    inline_keyboard=[[types.InlineKeyboardButton(text=buttons.cancel, callback_data="cancel")]]
)


class AdminService(BaseService):
    @staticmethod
    async def add_admin(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.answer(NAME_USER_ADMIN_ADD, reply_markup=cancel_keyboard)
        await state.set_state(AddAdminStates.name)
        await callback.message.delete()

    async def add_admin_name(self, message: types.Message, state: FSMContext):
        try:
            name = message.text.strip()
            if name.startswith("@"):
                name = name.strip("@")
            await self.table.update_by_tg_username(self.db_manager, name, **{"is_admin": True})
            await message.answer(SUCCESS_ADD_ADMIN % name)
            await state.clear()
        except ClientNotFound:
            await state.clear()
            await message.answer(ANSWER_NOT_FOUND_USER, reply_markup=cancel_keyboard)
            await state.set_state(AddAdminStates.name)
        except Conflict as e:
            await message.answer(e.args[0])
            await state.clear()
        except Exception as e:
            await message.answer(f"Ошибка: {e}. Попробуйте снова.")
            await state.clear()

    async def format_order_summary(self, order: OrdersOrm) -> str:
        text = f"📦 *Заказ #{order.id}*\n"
        text += f"👤 Пользователь: (@{order.user.tg_username or 'без имени'})\n"
        text += f"📍 Адрес доставки: {order.address.address}\n"
        text += f"📅 Дата: {order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else 'неизвестна'}\n"
        text += f"🚦 Статус: {order.status}\n"
        text += "🛒 Товары:\n"

        total_price = 0
        for item in order.items:
            product = item.product
            subtotal = product.price * item.quantity
            total_price += subtotal
            text += f"  - {product.name} x{item.quantity} = {subtotal} ₽\n"

        text += f"\n💰 *Итого:* {total_price} ₽\n"
        return text

    async def get_admin_orders_message(self) -> tuple[str, types.InlineKeyboardMarkup]:
        """
        Получает все заказы, форматирует их и возвращает текст и клавиатуру с кнопками управления.
        """
        async with self.db_manager.session() as session:
            orders = await session.scalars(
                select(OrdersOrm)
                .options(
                    selectinload(OrdersOrm.user),
                    selectinload(OrdersOrm.address),
                    selectinload(OrdersOrm.items).selectinload(OrderItemsOrm.product),
                )
                .order_by(OrdersOrm.created_at.desc())
            )
            orders = orders.all()

        if not orders:
            return "Нет заказов для отображения.", types.InlineKeyboardMarkup()

        text = "*Список заказов:*\n\n"
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])

        for order in orders:
            order_summary = await self.format_order_summary(order)
            text += order_summary + "\n" + ("-" * 30) + "\n"

            keyboard.inline_keyboard.append(
                [
                    types.InlineKeyboardButton(
                        text=f"📝 Управлять заказом #{order.id}",
                        callback_data=f"admin_order_manage:{order.id}",
                    )
                ]
            )

        return text, keyboard

    async def get_order_by_id(self, order_id: int) -> OrdersOrm | None:
        """
        Получает заказ по ID с загрузкой связанных данных (user, address, items с product).
        Возвращает OrdersOrm или None, если заказ не найден.
        """
        async with self.db_manager.session() as session:
            order = await session.scalar(
                select(OrdersOrm)
                .where(OrdersOrm.id == order_id)
                .options(
                    selectinload(OrdersOrm.user),
                    selectinload(OrdersOrm.address),
                    selectinload(OrdersOrm.items).selectinload(OrderItemsOrm.product),
                )
            )
            return order

    async def order_manage(self, callback: types.CallbackQuery, state: FSMContext):
        id = int(callback.data.split(":")[-1])
        order = await self.get_order_by_id(id)
        if not order:
            await callback.answer()
            await callback.message.answer(ORDER_NOT_FOUND, reply_markup=cancel_keyboard)
        await state.update_data(id=order.id)
        await callback.message.answer(ORDER_UPDATE_STATUS, reply_markup=cancel_keyboard)
        await state.set_state(UpdateStatusOrdersStates.status)
        await callback.message.delete()

    async def update_status(self, message: types.Message, state: FSMContext):
        status = message.text
        data = await state.get_data()
        await OrdersOrm.update_by_id(self.db_manager, int(data.get("id")), **{"status": status})
        await message.answer(SUCCESS_UPDATE_STATUS)
        await state.clear()

    async def viewing_orders(self, callback: types.CallbackQuery, state: FSMContext):
        text, keyboard = await self.get_admin_orders_message()
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=keyboard)


admin_service = AdminService(db_manager, UsersOrm)
