# handlers/subscription.py
import os
import re
from typing import Optional
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yookassa.domain.exceptions.bad_request_error import BadRequestError
from keyboards import kb_payment_pending

from states import Form
from texts import (
    PAYMENT_SUCCEEDED, PAYMENT_PENDING, PAYMENT_FAILED,
    STATUS_NOT_SET, STATUS_LINE, STATUS_PAID_TILL, STATUS_NEXT_CHARGE, STATUS_FOOTER,
    BTN_OPEN_PAYMENT, BTN_RETURN_TO_PAYMENT, BTN_CANCEL_PAYMENT, BTN_CHECK_PAYMENT,
    EMAIL_PROMPT, EMAIL_INVALID, SUBSCRIBE_CREATE, SUBSCRIBE_RESUME_FAIL, SUBSCRIBE_YK_REJECT, SUB_ALREADY_ACTIVE, CANCEL_ASK, CANCEL_ALREADY, CANCEL_DONE, CANCEL_NOT_ACTIVE, CANCEL_NONE,
    CANCEL_NEW_AFTER, BTN_CANCEL_YES, BTN_CANCEL_NO,
)
from billing.service import start_or_resume_checkout, check_and_activate, cancel_subscription, is_active
from db import (
    get_subscription, get_last_pending_payment_id, get_payment_confirmation_url,
    upsert_subscription, upsert_payment_status,
)

ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

#helper
async def _start_subscription_flow(reply, user_id: int, state: FSMContext, sub_row) -> None:
    from billing.service import start_or_resume_checkout, is_active
    if is_active(sub_row):
        cpe = sub_row[3] if sub_row else "-"
        cancelled_note = " (продление отключено)" if sub_row and sub_row[1] == "cancelled" else ""
        await reply(SUB_ALREADY_ACTIVE.format(cancelled=cancelled_note, cpe=cpe))
        return

    data = await state.get_data()
    sub_email = _extract_email_from_subscription_row(sub_row) or data.get("email")
    if not _valid_email(sub_email or ""):
        await state.update_data(next_flow="subscribe")
        await Form.email.set()
        await reply(EMAIL_PROMPT)
        return

    try:
        payment_id, url = await start_or_resume_checkout(user_id, email=sub_email)
    except BadRequestError as e:
        await reply(SUBSCRIBE_YK_REJECT.format(desc=getattr(e, "description", "invalid_request")))
        return
    except Exception:
        await reply(SUBSCRIBE_RESUME_FAIL)
        return

    kb = kb_payment_pending(payment_id, url)
    await reply(SUBSCRIBE_CREATE, reply_markup=kb)

def _valid_email(s: str) -> bool:
    return bool(_EMAIL_RE.match((s or "").strip()))

def _extract_email_from_subscription_row(sub) -> Optional[str]:
    if not sub:
        return None
    for x in sub:
        if isinstance(x, str) and "@" in x and " " not in x:
            return x
    return None

# --- commands ---
async def subscribe_cmd(message: types.Message, state: FSMContext) -> None:
    """Команда /subscribe — начать или продолжить оплату."""
    user_id = message.from_user.id
    sub = await get_subscription(user_id)
    if is_active(sub):
        cpe = sub[3] if sub else "-"
        cancelled_note = " (продление отключено)" if sub and sub[1] == "cancelled" else ""
        await message.answer(SUB_ALREADY_ACTIVE.format(cancelled=cancelled_note, cpe=cpe))
        return

    data = await state.get_data()
    sub_email = _extract_email_from_subscription_row(sub) or data.get("email")

    if not _valid_email(sub_email or ""):
        await state.update_data(next_flow="subscribe")
        await Form.email.set()
        await message.answer(EMAIL_PROMPT)
        return

    await _start_subscription_flow(message.answer, user_id, state, sub)

async def status_cmd(message: types.Message) -> None:
    user_id = message.from_user.id
    sub = await get_subscription(user_id)

    text_lines = []
    kb = InlineKeyboardMarkup()

    if not sub:
        text_lines.append(STATUS_NOT_SET)
    else:
        status = sub[1]
        cpe = sub[3] or "-"
        nca = sub[4] or "-"
        text_lines.append(STATUS_LINE.format(status=status))
        text_lines.append(STATUS_PAID_TILL.format(cpe=cpe))
        if status == "active":
            text_lines.append(STATUS_NEXT_CHARGE.format(nca=nca))

    pending_id = await get_last_pending_payment_id(user_id)
    if pending_id:
        url = await get_payment_confirmation_url(pending_id)
        kb = kb_payment_pending(pending_id, url)
        text_lines.append("\nЕсть незавершённый платёж.")

    text_lines.append(STATUS_FOOTER)
    await message.answer("\n".join(text_lines), reply_markup=kb if kb.inline_keyboard else None)

async def check_cmd(message: types.Message) -> None:
    payment_id = await get_last_pending_payment_id(message.from_user.id)
    if not payment_id:
        await message.answer("Нет платежей, ожидающих подтверждения. Используйте /subscribe, чтобы оформить подписку.")
        return
    try:
        result = await check_and_activate(message.from_user.id, payment_id)
    except BadRequestError as e:
        await message.answer(SUBSCRIBE_YK_REJECT.format(desc=getattr(e, "description", "invalid_request")))
        return

    if result == "succeeded":
        await message.answer(PAYMENT_SUCCEEDED)
    elif result == "pending":
        url = await get_payment_confirmation_url(payment_id)
        await message.answer(PAYMENT_PENDING, reply_markup=kb_payment_pending(payment_id, url))
    else:
        await message.answer(PAYMENT_FAILED)

# --- callbacks ---

async def subscribe_cb(call: types.CallbackQuery, state: FSMContext) -> None:
    """Колбэк 'go_subscribe' — начать/продолжить оформление подписки (с e-mail)."""
    await call.answer()
    user_id = call.from_user.id

    sub = await get_subscription(user_id)
    if is_active(sub):
        cpe = sub[3] if sub else "-"
        cancelled_note = " (продление отключено)" if sub and sub[1] == "cancelled" else ""
        await call.message.answer(SUB_ALREADY_ACTIVE.format(cancelled=cancelled_note, cpe=cpe))
        return

    data = await state.get_data()
    sub_email = _extract_email_from_subscription_row(sub) or data.get("email")
    if not _valid_email(sub_email or ""):
        await state.update_data(next_flow="go_subscribe")
        await Form.email.set()
        await call.message.answer(EMAIL_PROMPT)
        return

    await _start_subscription_flow(call.message.answer, user_id, state, sub)

async def cancel_payment_cb(call: types.CallbackQuery, state: FSMContext) -> None:
    """Колбэк 'cancelpay:{payment_id}' — пометить отмену и создать новый платёж (если есть e-mail)."""
    await call.answer()
    payment_id = call.data.split(":", 1)[1]
    user_id = call.from_user.id

    # помечаем платёж отменённым у себя
    await upsert_payment_status(user_id, payment_id, 0, "RUB", "canceled", raw_text='{"reason":"user_cancelled"}')

    sub = await get_subscription(user_id)
    data = await state.get_data()
    sub_email = _extract_email_from_subscription_row(sub) or data.get("email")

    if not _valid_email(sub_email or ""):
        await call.message.answer("Платёж отменён. Чтобы создать новый, отправьте /subscribe и укажите e-mail для чека.")
        return

    try:
        new_id, url = await start_or_resume_checkout(user_id, email=sub_email)
    except Exception:
        await call.message.answer(SUBSCRIBE_RESUME_FAIL)
        return

    await call.message.answer(CANCEL_NEW_AFTER, reply_markup=kb_payment_pending(new_id, url))

async def check_payment_cb(call: types.CallbackQuery) -> None:
    """Колбэк 'chkpay:{payment_id}' — проверить конкретный платёж."""
    await call.answer()
    payment_id = call.data.split(":", 1)[1]
    try:
        result = await check_and_activate(call.from_user.id, payment_id)
    except BadRequestError as e:
        await call.message.answer(SUBSCRIBE_YK_REJECT.format(desc=getattr(e, "description", "invalid_request")))
        return

    if result == "succeeded":
        await call.message.edit_text(PAYMENT_SUCCEEDED)
    elif result == "pending":
        url = await get_payment_confirmation_url(payment_id)
        await call.message.answer(PAYMENT_PENDING, reply_markup=kb_payment_pending(payment_id, url))
    else:
        await call.message.answer(PAYMENT_FAILED)

# --- email state ---

async def process_email_for_subscription(message: types.Message, state: FSMContext):
    """Пользователь прислал e-mail → сохраняем и создаём/возобновляем платёж."""
    user_id = message.from_user.id
    email = (message.text or "").strip()

    if not _valid_email(email):
        await message.answer(EMAIL_INVALID)
        return

    await upsert_subscription(user_id, email=email)
    await state.update_data(email=email)

    try:
        payment_id, url = await start_or_resume_checkout(user_id, email=email)
    except BadRequestError as e:
        await state.finish()
        await message.answer(SUBSCRIBE_YK_REJECT.format(desc=getattr(e, "description", "invalid_request")))
        return
    except Exception:
        await state.finish()
        await message.answer(SUBSCRIBE_RESUME_FAIL)
        return

    kb = InlineKeyboardMarkup().add(InlineKeyboardButton(BTN_OPEN_PAYMENT, url=url))
    kb.add(InlineKeyboardButton(BTN_CHECK_PAYMENT, callback_data=f"chkpay:{payment_id}"))
    kb.add(InlineKeyboardButton(BTN_CANCEL_PAYMENT, callback_data=f"cancelpay:{payment_id}"))
    await message.answer("Отлично! Создал оплату, нажмите кнопку ниже:", reply_markup=kb)
    await state.finish()

# --- cancel subscription command ---

async def cancel_cmd(message: types.Message):
    sub = await get_subscription(message.from_user.id)
    if not sub:
        await message.answer(CANCEL_NONE)
        return

    status, cpe = sub[1], sub[3]
    if not cpe:
        await message.answer(CANCEL_NOT_ACTIVE)
        return

    if status == "cancelled":
        await message.answer(CANCEL_ALREADY.format(cpe=cpe))
        return

    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(BTN_CANCEL_YES, callback_data="cancel_yes"),
        InlineKeyboardButton(BTN_CANCEL_NO, callback_data="cancel_no"),
    )
    await message.answer(CANCEL_ASK.format(cpe=cpe), reply_markup=kb)

async def cancel_yes_cb(call: types.CallbackQuery):
    await call.answer()
    await cancel_subscription(call.from_user.id)
    await call.message.edit_text(CANCEL_DONE)

async def cancel_no_cb(call: types.CallbackQuery):
    await call.answer("Оставили как есть ✅", show_alert=False)

# --- admin: set next_charge_at in Europe/Vienna ---

def _parse_local_datetime(s: str) -> datetime:
    s = s.strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            dt_naive = datetime.strptime(s, fmt)
            return dt_naive.replace(tzinfo=ZoneInfo("Europe/Vienna"))
        except ValueError:
            continue
    raise ValueError("Неверный формат даты. Используй 'YYYY-MM-DD HH:MM'.")

async def admin_next_charge_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Недостаточно прав.")
        return

    try:
        parts = message.text.strip().split(maxsplit=2)
        if len(parts) < 3:
            raise ValueError("Нужно 2 аргумента: <user_id> <YYYY-MM-DD HH:MM>")

        uid_str, dt_str = parts[1], parts[2]
        uid = int(uid_str)

        local_dt = _parse_local_datetime(dt_str)
        utc_dt = local_dt.astimezone(timezone.utc)

        await upsert_subscription(uid, next_charge_at=utc_dt.isoformat())

        sub = await get_subscription(uid)
        stored_nca = sub[4] if sub else None
        try:
            stored_utc = datetime.fromisoformat(stored_nca).replace(tzinfo=timezone.utc)
            stored_local = stored_utc.astimezone(ZoneInfo("Europe/Vienna")).strftime("%Y-%m-%d %H:%M")
        except Exception:
            stored_local = str(stored_nca)

        await message.answer(
            f"OK: next_charge_at для {uid} → {utc_dt.isoformat()} (UTC)\n"
            f"= {stored_local} (Europe/Vienna) — сохранено."
        )
    except Exception as e:
        await message.answer(
            f"Ошибка: {e}\n"
            "Пример: /admin_next_charge 197925837 2025-08-18 10:00"
        )

def register_subscription_handlers(dp: Dispatcher) -> None:
    # команды
    dp.register_message_handler(subscribe_cmd, commands="subscribe", state="*")
    dp.register_message_handler(status_cmd, commands="status", state="*")
    dp.register_message_handler(check_cmd, commands="check", state="*")
    dp.register_message_handler(cancel_cmd, commands="cancel", state="*")
    dp.register_message_handler(process_email_for_subscription, state=Form.email)

    # колбэки
    dp.register_callback_query_handler(subscribe_cb, lambda c: c.data == "go_subscribe", state="*")
    dp.register_callback_query_handler(cancel_payment_cb, lambda c: c.data.startswith("cancelpay:"), state="*")
    dp.register_callback_query_handler(check_payment_cb, lambda c: c.data.startswith("chkpay:"), state="*")
    dp.register_callback_query_handler(cancel_yes_cb, lambda c: c.data == "cancel_yes", state="*")
    dp.register_callback_query_handler(cancel_no_cb,  lambda c: c.data == "cancel_no", state="*")

    # админ
    dp.register_message_handler(admin_next_charge_cmd, commands="admin_next_charge", state="*")
