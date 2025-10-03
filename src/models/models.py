from typing import List

from sqlalchemy import ForeignKey, LargeBinary, UniqueConstraint, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.exceptions import ClientNotFound, Conflict
from core.logger import log
from models.base import BaseMixin


class CategoriesOrm(BaseMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    products: Mapped[List["ProductsOrm"]] = relationship(back_populates="category")


class ProductsOrm(BaseMixin):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str]
    price: Mapped[int] = mapped_column(nullable=False)
    photo: Mapped[bytes] = mapped_column(LargeBinary)
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped["CategoriesOrm"] = relationship(back_populates="products")

    cart: Mapped[List["CartOrm"]] = relationship(back_populates="product")
    order_items: Mapped[List["OrderItemsOrm"]] = relationship(back_populates="product")


class CartOrm(BaseMixin):
    __tablename__ = "cart"

    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)

    user: Mapped["UsersOrm"] = relationship(back_populates="cart")
    product: Mapped["ProductsOrm"] = relationship(back_populates="cart")

    __table_args__ = (UniqueConstraint("tg_id", "product_id", name="uq_user_product"),)


class OrdersOrm(BaseMixin):
    __tablename__ = "orders"

    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    status: Mapped[str] = mapped_column(default="pending", nullable=False)
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))

    user: Mapped["UsersOrm"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItemsOrm"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    address: Mapped["AddressesOrm"] = relationship(back_populates="orders")


class OrderItemsOrm(BaseMixin):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)

    order: Mapped["OrdersOrm"] = relationship(back_populates="items")
    product: Mapped["ProductsOrm"] = relationship(back_populates="order_items")


class UsersOrm(BaseMixin):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(unique=True)
    tg_username: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
    name: Mapped[str] = mapped_column(nullable=True)
    phone_number: Mapped[str] = mapped_column(nullable=True)

    cart: Mapped[List["CartOrm"]] = relationship(back_populates="user")
    orders: Mapped[List["OrdersOrm"]] = relationship(back_populates="user")
    addresses: Mapped[List["AddressesOrm"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("tg_id", "tg_username", name="uq_tg_id_tg_username"),)

    @classmethod
    async def update_by_tg_username(cls, db_manager, tg_username, **kwargs):
        async with db_manager.session() as session:
            try:
                query = select(cls).where(cls.tg_username == tg_username)
                result = await session.execute(query)
                result = result.scalar_one_or_none()
                if not result:
                    raise ClientNotFound
                await result.update(session, **kwargs)
                return result
            except IntegrityError as ex:
                await session.rollback()
                log.error("save", ex)
                raise Conflict(f"Integrity error: {ex}. Check for duplicate entries or constraint violations.") from ex


class AddressesOrm(BaseMixin):
    __tablename__ = "addresses"

    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["UsersOrm"] = relationship(back_populates="addresses")
    orders: Mapped[List["OrdersOrm"]] = relationship(back_populates="address")
