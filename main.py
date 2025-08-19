import os
import asyncio
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db import init_db, get_user_id_by_payment_id
from handlers import register_handlers
from billing.service import check_and_activate, charge_due_subscriptions


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
            # подтянем платёж через API и продлим при успехе
            await check_and_activate(uid, payment_id)
    return web.Response(text="ok")

async def _autobiller_loop():
    # каждые 10 минут пробуем списать у тех, кому пора
    while True:
        try:
            res = await charge_due_subscriptions()
            # можно логировать res
        except Exception as e:
            print("autobiller error:", e)
        await asyncio.sleep(60)  # 10 минут

bot = create_bot()
dp = Dispatcher(bot, storage=MemoryStorage())
register_handlers(dp)

if __name__ == '__main__':
    async def main():
        print("Bot started")
        await init_db()

        # веб-сервер для вебхука
        app = web.Application()
        app.router.add_post("/yookassa/webhook", yookassa_webhook)
        runner = web.AppRunner(app); await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "8080"))); await site.start()

        # фоновые автосписания
        asyncio.create_task(_autobiller_loop())

        await dp.start_polling()

    asyncio.run(main())