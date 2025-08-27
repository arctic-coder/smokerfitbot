# handlers/common.py
import os
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards import start_kb
from texts import (
    START_MESSAGE, NO_PENDING_PAYMENTS, PAYMENT_CHECK_FAILED,
    PAYMENT_SUCCEEDED, PAYMENT_PENDING, PAYMENT_FAILED,
    BTN_RETURN_TO_PAYMENT, BTN_CANCEL_PAYMENT,
)
from billing.service import check_and_activate
from db import get_last_pending_payment_id, get_payment_confirmation_url

ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))

def _payment_pending_kb(payment_id: str, url: str | None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    if url:
        kb.add(InlineKeyboardButton(BTN_RETURN_TO_PAYMENT, url=url))
    kb.add(InlineKeyboardButton(BTN_CANCEL_PAYMENT, callback_data=f"cancelpay:{payment_id}"))
    return kb

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
            await message.answer(PAYMENT_PENDING, reply_markup=_payment_pending_kb(payment_id, url))
        else:
            await message.answer(PAYMENT_FAILED)
        return

    await message.answer(START_MESSAGE, reply_markup=start_kb)

def register_common_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start_cmd, commands="start", state="*")
