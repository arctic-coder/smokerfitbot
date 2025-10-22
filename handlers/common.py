# handlers/common.py
import os
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from keyboards import kb_payment_pending, start_button_kb, start_kb
from texts import (
    HELP, START_MESSAGE, NO_PENDING_PAYMENTS, PAYMENT_CHECK_FAILED,
    PAYMENT_SUCCEEDED, PAYMENT_PENDING, PAYMENT_FAILED,
    BTN_START,
)
from billing.service import check_and_activate
from db import get_last_pending_payment_id, get_payment_confirmation_url

ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))

async def help_cmd(message: types.Message, state: FSMContext) -> None:
        await message.answer(HELP)

async def start_cmd(message: types.Message, state: FSMContext) -> None:
    """Приветствие и deep-link 'payment_success': /start payment_success"""
    await state.finish()
    payload = message.get_args()

    if payload == "payment_success":
        user_id = message.from_user.id
        payment_id = await get_last_pending_payment_id(user_id)
        if not payment_id:
            await message.answer(NO_PENDING_PAYMENTS)
            return
        try:
            result = await check_and_activate(user_id, payment_id)
        except Exception:
            await message.answer(PAYMENT_CHECK_FAILED)
            return

        if result == "succeeded":
            await message.answer(PAYMENT_SUCCEEDED)
        elif result == "pending":
            url = await get_payment_confirmation_url(payment_id)
            await message.answer(PAYMENT_PENDING, reply_markup=kb_payment_pending(payment_id, url))
        else:
            await message.answer(PAYMENT_FAILED)
        return

    markup = start_kb if message.text == BTN_START else start_button_kb
    await message.answer(START_MESSAGE, parse_mode="HTML", disable_web_page_preview=True, reply_markup=markup)

def register_common_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start_cmd, lambda m: m.text == BTN_START, state="*")
    dp.register_message_handler(start_cmd, commands="start", state="*")
    dp.register_message_handler(help_cmd, commands="help", state="*")
