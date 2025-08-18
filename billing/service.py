from datetime import datetime, timedelta
from db import upsert_subscription, upsert_payment_status, get_last_pending_payment_id  
from billing.yookassa_client import create_checkout_payment, get_payment

def _next_month(dt: datetime) -> datetime:
    month = dt.month + 1
    year = dt.year + (1 if month > 12 else 0)
    month = month if month <= 12 else 1
    return dt.replace(year=year, month=month)

async def start_subscription(user_id: int, email: str | None, phone: str | None):
    payment_id, url = create_checkout_payment(user_id, email, phone)
    await upsert_payment_status(user_id, payment_id, 0, "RUB", "pending", raw_text="{}")
    return payment_id, url

async def check_and_activate(user_id: int, payment_id: str):
    p = get_payment(payment_id)
    amount_int = int(round(float(p.amount.value) * 100))
    await upsert_payment_status(user_id, payment_id, amount_int, p.amount.currency, p.status, raw_text=p.json())

    if p.status == "succeeded":
        pm_id = None
        if p.payment_method and getattr(p.payment_method, "saved", False):
            pm_id = p.payment_method.id
        now = datetime.utcnow()
        await upsert_subscription(
            user_id,
            status="active",
            payment_method_id=pm_id,
            current_period_end=_next_month(now),
            next_charge_at=_next_month(now),
            amount=amount_int,
            currency=p.amount.currency
        )
        return "succeeded"

    if p.status in ("pending", "waiting_for_capture"):
        return "pending"

    # canceled / failed
    return "failed"


async def cancel_subscription(user_id: int):
    # помечаем как cancelled, но период не трогаем
    await upsert_subscription(user_id, status="cancelled")


def is_active(sub_row) -> bool:
    if not sub_row:
        return False
    # sub_row: (user_id, status, payment_method_id, current_period_end, next_charge_at, amount, currency, created_at, updated_at)
    status = sub_row[1]
    cpe = sub_row[3]
    if not cpe:
        return False
    # для SQLite дата — строка ISO
    if isinstance(cpe, str):
        try:
            cpe_dt = datetime.fromisoformat(cpe)
        except Exception:
            return False
    else:
        cpe_dt = cpe
    return status in ("active", "cancelled") and cpe_dt > datetime.utcnow()


def _get_confirmation_url(p):
    try:
        return getattr(getattr(p, "confirmation", None), "confirmation_url", None)
    except Exception:
        return None

async def start_or_resume_checkout(user_id: int, email: str | None, phone: str | None):
    """
    Если есть pending — вернём ссылку на оплату для существующего платежа.
    Если нет — создадим новый платеж.
    """
    last_pending = await get_last_pending_payment_id(user_id)
    if last_pending:
        p = get_payment(last_pending)
        if p and p.status in ("pending", "waiting_for_capture"):
            url = _get_confirmation_url(p)
            if url:
                return last_pending, url  # возобновляем оплату
        # если ссылки нет (редко), создадим новый платёж ниже

    # создаём новый платёж
    payment_id, url = create_checkout_payment(user_id, email, phone)
    await upsert_payment_status(user_id, payment_id, 0, "RUB", "pending", raw_text="{}")
    return payment_id, url

