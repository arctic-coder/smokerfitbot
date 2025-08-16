import json
from datetime import datetime, timedelta
from db import upsert_subscription, get_subscription, insert_payment
from billing.yookassa_client import create_checkout_payment, get_payment, create_recurring_payment

def _next_month(dt: datetime) -> datetime:
    # простой расчёт "через 1 месяц" — MVP
    month = dt.month + 1
    year = dt.year + (1 if month > 12 else 0)
    month = month if month <= 12 else 1
    return dt.replace(year=year, month=month)

async def start_subscription(user_id: int, email: str | None, phone: str | None):
    payment_id, url = create_checkout_payment(user_id, email, phone)
    await insert_payment(user_id, payment_id, 0, "RUB", "pending", raw_text="{}")
    # пометим подписку как trial/pending (не обязательно)
    await upsert_subscription(user_id, status="trial")
    return payment_id, url

async def check_and_activate(user_id: int, payment_id: str):
    p = get_payment(payment_id)
    await insert_payment(user_id, payment_id, int(float(p.amount.value) * 100), p.amount.currency, p.status, raw_text=json.dumps(p.json(), ensure_ascii=False))
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
            amount=int(float(p.amount.value) * 100),
            currency=p.amount.currency
        )
        return True
    return False

async def cancel_subscription(user_id: int):
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
    return status == "active" and cpe_dt > datetime.utcnow()
