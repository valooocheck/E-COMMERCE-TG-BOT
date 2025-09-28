import asyncio
import datetime
from typing import Annotated

from sqlalchemy import Integer, select, text
from sqlalchemy.exc import DataError, IntegrityError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from common.exceptions import Conflict, DatabaseError, DatabaseErrorDataOrConstrains, UpdateDatabaseError
from core.logger import log

intpk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
last_interaction = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    ),
]


class Base(DeclarativeBase):
    def log_error(self, action: str, ex: Exception):
        log.error(f"Error during {action} for {self.__tablename__}: {ex}")

    @classmethod
    def _build_query(cls, where_conditions=None):
        conditions = []
        if where_conditions:
            conditions.extend(where_conditions)
        return conditions

    @classmethod
    async def find_all(cls, db_manager, where_conditions=None, limit=None, offset=None):
        async with db_manager.session() as session:
            query = select(cls)
            conditions = cls._build_query(where_conditions)
            query = query.where(*conditions)
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_id(cls, db_manager, record_id):
        async with db_manager.session() as session:
            query = select(cls).where(cls.id == record_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def save(self, db_manager):
        async with db_manager.session() as session:
            try:
                session.add(self)
                await asyncio.shield(session.commit())
                await session.refresh(self)
            except IntegrityError as ex:
                await session.rollback()
                self.log_error("save", ex)
                raise Conflict(f"Integrity error: {ex}. Check for duplicate entries or constraint violations.") from ex
            except DataError as ex:
                await session.rollback()
                self.log_error("save", ex)
                raise DatabaseErrorDataOrConstrains(f"Data error: {ex}. Check data types and constraints.") from ex
            except SQLAlchemyError as ex:
                await session.rollback()
                self.log_error("save", ex)
                raise DatabaseError(f"Database error: {ex}") from ex

    @classmethod
    async def update_by_id(cls, db_manager, record_id, **kwargs):
        async with db_manager.session() as session:
            try:
                query = select(cls).where(cls.id == record_id)
                result = await session.execute(query)
                result = result.scalar_one_or_none()
                await result.update(session, **kwargs)
                return result
            except IntegrityError as ex:
                await session.rollback()
                log.error("save", ex)
                raise Conflict(f"Integrity error: {ex}. Check for duplicate entries or constraint violations.") from ex

    @classmethod
    async def delete_by_id(cls, db_manager, record_id: int):
        async with db_manager.session() as session:
            query = select(cls).where(cls.id == record_id)
            result = await session.execute(query)
            result = result.scalar_one_or_none()
            await result.hard_delete(session)

    async def update(self, session, **kwargs):
        try:
            for k, v in kwargs.items():
                if hasattr(self, k):
                    setattr(self, k, v)
                else:
                    raise ValueError(f"Атрибут {k} не существует в модели {self.__class__.__name__}")
            await session.commit()
            await session.refresh(self)
        except SQLAlchemyError as ex:
            await session.rollback()
            self.log_error("update", ex)
            raise UpdateDatabaseError(f"Error during update: {ex}") from ex

    async def hard_delete(self, session):
        try:
            await session.delete(self)
            await session.commit()
        except SQLAlchemyError as ex:
            await session.rollback()
            self.log_error("hard_delete", ex)


class BaseMixin(Base):
    id: Mapped[intpk]
    created_at: Mapped[created_at]

    __abstract__ = True
