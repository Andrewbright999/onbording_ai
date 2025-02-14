# main.py
import asyncio, logging, sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from handlers import router as handlers_router
from database import create_tables, drop_tables
from debug_test_handlers import router_debug

from db_fsm_storage import DBFSMStorage

from middleware import PrintStateMiddleware
# , DebugUpdateMiddleware  # импортируем middleware


logging.basicConfig(level=logging.INFO)


async def main():
    # await drop_tables()
    # Создаём таблицы, если их ещё нет
    await create_tables()
    
    storage = DBFSMStorage()  # Используем наше хранилище, которое работает через БД
    # dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token=BOT_TOKEN,
                default=DefaultBotProperties(
                parse_mode=ParseMode.HTML)
            )
    dp = Dispatcher(storage=storage)
    # dp.include_router(router_debug)
    dp.include_router(handlers_router)
    # dp.update.outer_middleware(PrintStateMiddleware())
    # dp.update.outer_middleware(DebugUpdateMiddleware())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())
