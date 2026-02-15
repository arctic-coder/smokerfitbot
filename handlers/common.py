# handlers/common.py
import os

from aiogram import Router, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from billing.service import check_and_activate
from db import get_last_pending_payment_id, get_payment_confirmation_url
from keyboards import kb_payment_pending, start_kb
from texts import (
    HELP,
    NO_PENDING_PAYMENTS,
    PAYMENT_CHECK_FAILED,
    PAYMENT_FAILED,
    PAYMENT_PENDING,
    PAYMENT_SUCCEEDED,
    START_MESSAGE,
)

ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))

common_router = Router()


async def send_start_screen(message: types.Message, state: FSMContext) -> None:
    """Shared helper: clear state and show the start screen with keyboard."""
    await state.clear()
    await message.answer(START_MESSAGE, parse_mode="HTML", disable_web_page_preview=True, reply_markup=start_kb)


@common_router.message(CommandStart(), StateFilter("*"))
async def start_cmd(message: types.Message, state: FSMContext, command: CommandStart) -> None:
    """Greeting and deep-link 'payment_success': /start payment_success"""
    await state.clear()
    payload = command.args

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

    await message.answer(START_MESSAGE, parse_mode="HTML", disable_web_page_preview=True, reply_markup=start_kb)


@common_router.message(Command("help"), StateFilter("*"))
async def help_cmd(message: types.Message) -> None:
    await message.answer(HELP)
