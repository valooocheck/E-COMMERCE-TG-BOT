from typing import List

from sqlalchemy import ForeignKey, LargeBinary, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseMixin


class CategoriesOrm(BaseMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    products: Mapped[List["ProductsOrm"]] = relationship(back_populates="category")


class ProductsOrm(BaseMixin):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str]
    price: Mapped[float] = mapped_column(nullable=False)
    photo: Mapped[bytes] = mapped_column(LargeBinary)
    quantity: Mapped[int] = mapped_column(default=0, nullable=False)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped["CategoriesOrm"] = relationship(back_populates="products")


class UsersOrm(BaseMixin):
    __tablename__ = "users"

    tg_id: Mapped[int]
    tg_username: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text("false"))
    name: Mapped[str] = mapped_column(nullable=True)
    phone_number: Mapped[str] = mapped_column(nullable=True)

    __table_args__ = (UniqueConstraint("tg_id", "tg_username", name="uq_tg_id_tg_username"),)
