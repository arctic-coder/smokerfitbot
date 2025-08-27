import os
import asyncio
import signal
import contextlib
import logging

from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db import init_db, get_user_id_by_payment_id
from handlers import register_handlers
from billing.service import check_and_activate, charge_due_subscriptions


log = logging.getLogger("app")


def create_bot() -> Bot:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")
    return Bot(token=token)


# --- YooKassa webhook ---------------------------------------------------------

# Приём веб-хуков о статусах платежей (НЕ telegram webhook!)
async def yookassa_webhook(request: web.Request):
    try:
        data = await request.json()
    except Exception:
        return web.Response(status=400, text="bad json")

    # ожидаем форму {"event": "...", "object": {"id": "pay_...", "status": "...", ...}}
    payment = (data or {}).get("object") or {}
    payment_id = payment.get("id")
    if payment_id:
        try:
            uid = await get_user_id_by_payment_id(payment_id)
            if uid:
                await check_and_activate(uid, payment_id)
        except Exception as e:
            log.exception("yookassa_webhook failed: %s", e)
            # возвращаем 200/ok, чтобы YooKassa не спамила ретраями
    return web.Response(text="ok")


# --- Фоновая задача: автосписания --------------------------------------------

async def _autobiller_loop():
    # Каждые 10 минут пробуем списать у тех, кому пора
    while True:
        try:
            res = await charge_due_subscriptions()
            # при желании логируйте результат: log.info("autobiller: %s", res)
        except Exception as e:
            log.exception("autobiller error: %s", e)
        await asyncio.sleep(600)  # 10 минут


# --- Приложение ---------------------------------------------------------------

async def main():
    # базовая инициализация
    load_dotenv()
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    log.info("Starting bot...")

    await init_db()

    bot = create_bot()
    dp = Dispatcher(bot, storage=MemoryStorage())
    register_handlers(dp)  # из handlers/__init__.py

    # HTTP-сервер только для вебхука YooKassa
    app = web.Application()
    app.router.add_post("/yookassa/webhook", yookassa_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "8080")))
    await site.start()
    log.info("Webhook server started on /yookassa/webhook")

    # фоновые автосписания
    autobiller_task = asyncio.create_task(_autobiller_loop(), name="autobiller")

    # аккуратное завершение по сигналам
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _stop(*_):
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, _stop)

    try:
        # telegram long polling — блокирующий вызов пока идёт работа бота
        await dp.start_polling()
    finally:
        # гасим фоновые задачи и HTTP-сервер
        autobiller_task.cancel()
        with contextlib.suppress(Exception):
            await autobiller_task
        await runner.cleanup()
        await bot.session.close()
        log.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
