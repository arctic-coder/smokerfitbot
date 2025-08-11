import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db import init_db
from handlers import register_handlers
import asyncio

def create_bot() -> Bot:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")
    return Bot(token=token)

bot = create_bot()
dp = Dispatcher(bot, storage=MemoryStorage())
register_handlers(dp)

if __name__ == '__main__':
    async def main():
        print("Bot started")
        await init_db()
        await dp.start_polling()

    asyncio.run(main())