# handlers/subscription.py
import os
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from yookassa.domain.exceptions.bad_request_error import BadRequestError

from billing.service import cancel_subscription, check_and_activate, is_active, start_or_resume_checkout
from billing.yookassa_client import amount_for
from db import (
    get_active_promocode,
    get_last_pending_payment_id,
    get_payment_confirmation_url,
    get_subscription,
    has_active_promocodes,
    upsert_payment_status,
    upsert_subscription,
)
from handlers.common import send_start_screen
from keyboards import kb_choose_plan, kb_choose_plan_with_prices, kb_payment_pending, kb_promo_prompt
from states import Form
from texts import (
    BTN_CANCEL_NO,
    BTN_CANCEL_YES,
    CANCEL_ALREADY,
    CANCEL_ASK,
    CANCEL_CURRENT,
    CANCEL_DONE,
    CANCEL_NONE,
    CANCEL_NOT_ACTIVE,
    EMAIL_INVALID,
    EMAIL_PROMPT,
    PAYMENT_FAILED,
    PAYMENT_PENDING,
    PAYMENT_SUCCEEDED,
    PROMO_APPLIED,
    PROMO_INVALID,
    PROMO_PROMPT,
    STATUS_FOOTER,
    STATUS_LINE,
    STATUS_NEXT_CHARGE,
    STATUS_NOT_SET,
    STATUS_PAID_TILL,
    SUB_ALREADY_ACTIVE,
    SUBSCRIBE_CREATE,
    SUBSCRIBE_FROM_COMMAND,
    SUBSCRIBE_RESUME_FAIL,
    SUBSCRIBE_YK_REJECT,
)

subscription_router = Router()

ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

# helper


def _date_only(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m-%d") if dt else "-"


async def _start_subscription_flow(reply, user_id: int, state: FSMContext, sub_row) -> None:
    if is_active(sub_row, include_cancelled=False):
        cpe = _date_only(sub_row[3] if sub_row else None)
        cancelled_note = " (продление отключено)" if sub_row and sub_row[1] == "cancelled" else ""
        await reply(SUB_ALREADY_ACTIVE.format(cancelled=cancelled_note, cpe=cpe))
        return

    data = await state.get_data()
    sub_email = _extract_email_from_subscription_row(sub_row) or data.get("email")
    if not _valid_email(sub_email or ""):
        await state.set_state(Form.email)
        await reply(EMAIL_PROMPT)
        return

    try:
        data = await state.get_data()
        plan = data.get("plan") or "month"
        price_override, promo_code, promo_title = _promo_params_for_plan(data, plan)
        payment_id, url = await start_or_resume_checkout(
            user_id,
            email=sub_email,
            plan=plan,
            price_override_cents=price_override,
            promo_code=promo_code,
            promo_title=promo_title,
        )
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


def _extract_email_from_subscription_row(sub) -> str | None:
    if not sub:
        return None
    for x in sub:
        if isinstance(x, str) and "@" in x and " " not in x:
            return x
    return None


def _promo_params_for_plan(data: dict, plan: str) -> tuple[int | None, str | None, str | None]:
    promo_code = data.get("promo_code")
    promo_title = data.get("promo_title")
    price_override = None
    if promo_code:
        key = "promo_price_year_cents" if plan == "year" else "promo_price_month_cents"
        try:
            price_override = int(data.get(key)) if data.get(key) is not None else None
        except Exception:
            price_override = None
    return price_override, promo_code, promo_title


# --- commands ---
@subscription_router.message(Command("subscribe"), StateFilter("*"))
async def subscribe_cmd(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    sub = await get_subscription(user_id)
    if not is_active(sub, include_cancelled=False):
        await state.update_data(
            plan=None,
            promo_code=None,
            promo_title=None,
            promo_price_month_cents=None,
            promo_price_year_cents=None,
        )
        if await has_active_promocodes():
            await state.set_state(Form.promo)
            await message.answer(PROMO_PROMPT, reply_markup=kb_promo_prompt())
        else:
            await message.answer(SUBSCRIBE_FROM_COMMAND, reply_markup=kb_choose_plan())
    else:  # already active subscription
        cpe = _date_only(sub[3] if sub else None)
        cancelled_note = " (продление отключено)" if sub and sub[1] == "cancelled" else ""
        await message.answer(SUB_ALREADY_ACTIVE.format(cancelled=cancelled_note, cpe=cpe))
        return


@subscription_router.message(Form.promo)
async def process_promo_code(message: types.Message, state: FSMContext) -> None:
    code = (message.text or "").strip()
    if not code:
        await message.answer(PROMO_INVALID, reply_markup=kb_promo_prompt())
        return

    promo = await get_active_promocode(code)
    if not promo:
        await message.answer(PROMO_INVALID, reply_markup=kb_promo_prompt())
        return

    _, title, _, _, price_month, price_year, _ = promo
    await state.update_data(
        promo_code=promo[0],
        promo_title=title,
        promo_price_month_cents=price_month,
        promo_price_year_cents=price_year,
        plan=None,
    )
    await message.answer(PROMO_APPLIED, reply_markup=kb_choose_plan_with_prices(price_month, price_year))


@subscription_router.callback_query(F.data == "promo_skip", StateFilter("*"))
async def promo_skip_cb(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.update_data(
        promo_code=None,
        promo_title=None,
        promo_price_month_cents=None,
        promo_price_year_cents=None,
        plan=None,
    )
    await call.message.edit_text(SUBSCRIBE_FROM_COMMAND, reply_markup=kb_choose_plan())


@subscription_router.message(Command("status"), StateFilter("*"))
async def status_cmd(message: types.Message) -> None:
    user_id = message.from_user.id
    sub = await get_subscription(user_id)

    text_lines = []
    kb = None

    if not sub:
        text_lines.append(STATUS_NOT_SET)
    else:
        status = sub[1]
        cpe = _date_only(sub[3] if sub else None)
        nca = _date_only(sub[4] if sub else None)
        plan = (sub[10] if len(sub) > 10 else None) or "month"
        text_lines.append(STATUS_LINE.format(status=status))
        text_lines.append(STATUS_PAID_TILL.format(cpe=cpe))
        if status == "active":
            _, amount_value, _ = amount_for(plan)
            text_lines.append(STATUS_NEXT_CHARGE.format(nca=nca, amount=amount_value))

    pending_id = await get_last_pending_payment_id(user_id)
    if pending_id:
        url = await get_payment_confirmation_url(pending_id)
        kb = kb_payment_pending(pending_id, url)
        text_lines.append("\nЕсть незавершённый платёж.")

    text_lines.append(STATUS_FOOTER)
    # Always show keyboard (payment pending or choose plan)
    if kb is None:
        kb = kb_choose_plan()
    await message.answer("\n".join(text_lines), reply_markup=kb)


# --- callbacks ---


@subscription_router.callback_query(F.data.startswith("go_subscribe"), StateFilter("*"))
async def subscribe_cb(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    parts = (call.data or "").split(":", 1)
    plan = parts[1] if len(parts) == 2 else "month"
    await state.update_data(plan=plan)
    user_id = call.from_user.id
    sub = await get_subscription(user_id)
    await _start_subscription_flow(call.message.answer, user_id, state, sub)


@subscription_router.callback_query(F.data.startswith("cancelpay:"), StateFilter("*"))
async def cancel_payment_cb(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    payment_id = call.data.split(":", 1)[1]
    user_id = call.from_user.id

    await upsert_payment_status(user_id, payment_id, 0, "RUB", "canceled", raw_text='{"reason":"user_cancelled"}')

    await call.message.answer(CANCEL_CURRENT)
    await send_start_screen(call.message, state)


@subscription_router.callback_query(F.data.startswith("chkpay:"), StateFilter("*"))
async def check_payment_cb(call: types.CallbackQuery, state: FSMContext) -> None:
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
        await send_start_screen(call.message, state)
    elif result == "pending":
        url = await get_payment_confirmation_url(payment_id)
        await call.message.answer(PAYMENT_PENDING, reply_markup=kb_payment_pending(payment_id, url))
    else:
        await call.message.answer(PAYMENT_FAILED)
        await send_start_screen(call.message, state)


# --- email state ---


@subscription_router.message(Form.email)
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
        data = await state.get_data()
        plan = data.get("plan") or "month"
        price_override, promo_code, promo_title = _promo_params_for_plan(data, plan)
        payment_id, url = await start_or_resume_checkout(
            user_id,
            email=email,
            plan=plan,
            price_override_cents=price_override,
            promo_code=promo_code,
            promo_title=promo_title,
        )
    except BadRequestError as e:
        await state.clear()
        await message.answer(SUBSCRIBE_YK_REJECT.format(desc=getattr(e, "description", "invalid_request")))
        return
    except Exception:
        await state.clear()
        await message.answer(SUBSCRIBE_RESUME_FAIL)
        return

    await message.answer(
        "Отлично! Создал оплату, нажмите кнопку ниже:", reply_markup=kb_payment_pending(payment_id, url)
    )
    await state.clear()


# --- cancel subscription command ---


@subscription_router.message(Command("cancel"), StateFilter("*"))
async def cancel_cmd(message: types.Message):
    sub = await get_subscription(message.from_user.id)
    if not sub:
        await message.answer(CANCEL_NONE)
        return

    status = sub[1]
    cpe = _date_only(sub[3] if sub else None)
    if not cpe:
        await message.answer(CANCEL_NOT_ACTIVE)
        return

    if status == "cancelled":
        await message.answer(CANCEL_ALREADY.format(cpe=cpe))
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=BTN_CANCEL_YES, callback_data="cancel_yes"),
                InlineKeyboardButton(text=BTN_CANCEL_NO, callback_data="cancel_no"),
            ]
        ]
    )
    await message.answer(CANCEL_ASK.format(cpe=cpe), reply_markup=kb)


@subscription_router.callback_query(F.data == "cancel_yes", StateFilter("*"))
async def cancel_yes_cb(call: types.CallbackQuery):
    await call.answer()
    await cancel_subscription(call.from_user.id)
    await call.message.edit_text(CANCEL_DONE)


@subscription_router.callback_query(F.data == "cancel_no", StateFilter("*"))
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


@subscription_router.message(Command("admin_next_charge"), StateFilter("*"))
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
            f"OK: next_charge_at для {uid} → {utc_dt.isoformat()} (UTC)\n= {stored_local} (Europe/Vienna) — сохранено."
        )
    except Exception as e:
        await message.answer(f"Ошибка: {e}\nПример: /admin_next_charge 197925837 2025-08-18 10:00")
