import datetime
from functools import wraps

from aiogram import types
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError

from buttons.buttons import NOT_ADMIN
from common.exceptions import ClientNotFound
from core.logger import log
from db import db_manager
from models.models import UsersOrm


class DBInteraction:
    def __init__(self, db_man, table, logger):
        self.db_manager = db_man
        self.table: UsersOrm = table
        self.log = logger

    def __call__(self, func):
        @wraps(func)
        async def wrapper(callback: types.CallbackQuery, *args, **kwargs):
            user = callback.from_user

            await func(callback, *args, **kwargs)

            async with self.db_manager.session() as session:
                try:
                    await session.execute(insert(UsersOrm).values(tg_id=user.id, tg_username=user.username))
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
                    log.warning(f"User {user.username} is already added to the table!")
            return

        return wrapper

    def check_admin(self, func):
        @wraps(func)
        async def wrapper(callback: types.CallbackQuery, *args, **kwargs):
            user = callback.from_user
            async with self.db_manager.session() as session:
                stmt = select(self.table).where(UsersOrm.tg_id == user.id)
                res = await session.execute(stmt)
                user_orm: UsersOrm = res.scalars().first()
            if not user_orm:
                raise ClientNotFound("User not found in database")
            if not user_orm.is_admin:
                if isinstance(callback, types.Message):
                    return callback.answer(NOT_ADMIN)
                return callback.message.answer(NOT_ADMIN)

            return await func(callback, *args, **kwargs)

        return wrapper


db_interaction = DBInteraction(db_manager, UsersOrm, log)
