import logging, os
import asyncio
import signal
import contextlib
import json

from aiohttp import web
from config import Config
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db import init_db, get_user_id_by_payment_id
from handlers import register_handlers
from billing.service import check_and_activate, charge_due_subscriptions
from jobs.autobiller import autobiller_loop
from logging_setup import setup_logging
from texts import RECURRING_FAILED_RETRY, RECURRING_FAILED_RETRY_LAST, RECURRING_PRECHARGE, RECURRING_SUCCESS
from web.yk_handlers import yookassa_webhook

log = logging.getLogger("main")

def create_bot(token: str) -> Bot:
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")
    return Bot(token=token)


async def main():
    load_dotenv()
    cfg = Config.from_env();
    setup_logging(cfg.log_level)
    log.info("Starting bot...")

    await init_db()

    bot = create_bot(cfg.bot_token)
    dp = Dispatcher(bot, storage=MemoryStorage())
    register_handlers(dp)  # handlers/__init__.py

    # HTTP server for webhook from yookasssa
    app = web.Application(client_max_size=cfg.client_max_size)
    app.router.add_post("/yookassa/webhook", yookassa_webhook)
    app.router.add_get("/healthz", lambda r: web.Response(text="ok"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", "8080")))
    await site.start()
    log.info("Webhook server started on /yookassa/webhook")

    # start scheduled task - reccurent payments
    async def tg_notify(user_id: int, kind: str, ctx: dict):
        try:
            if kind == "precharge":
                await bot.send_message(user_id, RECURRING_PRECHARGE)
            elif kind == "charged_success":
                await bot.send_message(user_id, RECURRING_SUCCESS)
            elif kind == "charged_failed":
                await bot.send_message(user_id, RECURRING_FAILED_RETRY)
            elif kind == "charged_failed_last":
                await bot.send_message(user_id, RECURRING_FAILED_RETRY_LAST)
        except Exception:
            log.exception("notify failed user_id=%s kind=%s", user_id, kind)

    autobiller_task = asyncio.create_task(autobiller_loop(cfg.autobill_interval_sec, notifier=tg_notify), name="autobiller")

    # quit
    try:
        await dp.start_polling()
    finally:
        autobiller_task.cancel()
        with contextlib.suppress(Exception):
            await autobiller_task
        await runner.cleanup()
        await bot.session.close()
        
        from db import close_db
        try:
            await close_db()
        except Exception as e:
            log.exception("Error closing DB pool: %s", e)
        log.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
