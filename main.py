import os
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
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

async def yookassa_webhook(request: web.Request):
    try:
        data = await request.json()
    except Exception:
        return web.Response(status=400, text="bad json")
    payment_id = data.get("object", {}).get("id")
    if payment_id:
        uid = await get_user_id_by_payment_id(payment_id)
        if uid:
            await check_and_activate(uid, payment_id)  # подтягиваем платёж через API внутри
    return web.Response(text="ok")

bot = create_bot()
dp = Dispatcher(bot, storage=MemoryStorage())
register_handlers(dp)

if __name__ == '__main__':
    async def main():
        print("Bot started")
        await init_db()

        # поднимем простой веб-сервер для вебхука
        app = web.Application()
        app.router.add_post("/yookassa/webhook", yookassa_webhook)
        runner = web.AppRunner(app); await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "8080"))); await site.start()

        await dp.start_polling()

    asyncio.run(main())