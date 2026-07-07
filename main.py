import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.handlers.admin import admin_router
from app.handlers.booking import booking_router
from app.handlers.client import client_router
from config import Settings, get_settings
from database import init_db


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    settings: Settings = get_settings()
    init_db(settings.database_path)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    dp['settings'] = settings
    dp.include_router(client_router)
    dp.include_router(booking_router)
    dp.include_router(admin_router)

    logging.info('BeautyBot Pro started')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
