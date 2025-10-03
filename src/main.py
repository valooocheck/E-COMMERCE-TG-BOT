import asyncio

from aiogram import Bot, Dispatcher

from core.config import config
from core.logger import log
from db import db_manager
from handlers import routers


async def main():
    db_manager.init(config.postgres.dsn)
    bot = Bot(token=config.telegram_bot.token.get_secret_value())
    dp = Dispatcher()

    dp.include_routers(*routers)
    log.info("Your service has started")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
