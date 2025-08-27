from datetime import datetime, timedelta, timezone
from db import (
    upsert_subscription, upsert_payment_status, get_last_pending_payment_id,
    get_payment_confirmation_url, get_subscription, insert_payment, mark_payment_applied, cancel_other_pendings 
)
from billing.yookassa_client import create_checkout_payment, get_payment, create_recurring_payment

def _next_month(dt: datetime) -> datetime:
    month = dt.month + 1
    year = dt.year + (1 if month > 12 else 0)
    month = month if month <= 12 else 1
    try:
        return dt.replace(year=year, month=month)
    except ValueError:
        return dt.replace(year=year, month=month, day=28)

def _extract_email_from_subscription_row(sub) -> str | None:
    """
    Извлекаем email из кортежа подписки без жёсткой завязки на позицию поля.
    Возвращает None, если email не найден.
    """
    if not sub:
        return None
    for x in sub:
        if isinstance(x, str) and "@" in x and " " not in x:
            return x
    return None


def _calc_renewal_dates(current_period_end, now_utc: datetime):
    """
    Возвращает (new_cpe, next_charge_at):
    - если текущий период ещё активен, считаем от current_period_end;
    - если истёк — считаем от now.
    Гарантируем работу только с UTC-aware datetime.
    """
    # нормализуем current_period_end к UTC-aware datetime
    if isinstance(current_period_end, str):
        try:
            cpe_dt = datetime.fromisoformat(current_period_end.replace("Z", "+00:00"))
        except Exception:
            cpe_dt = None
    else:
        cpe_dt = current_period_end

    if cpe_dt is not None:
        if cpe_dt.tzinfo is None:
            cpe_dt = cpe_dt.replace(tzinfo=timezone.utc)
        else:
            cpe_dt = cpe_dt.astimezone(timezone.utc)

    anchor = cpe_dt if (cpe_dt and cpe_dt > now_utc) else now_utc
    new_cpe = _next_month(anchor)
    next_charge_at = new_cpe - timedelta(days=1)
    return new_cpe, next_charge_at

def _get_confirmation_url(p):
    try:
        return getattr(getattr(p, "confirmation", None), "confirmation_url", None)
    except Exception:
        return None
    

# service.py
async def check_and_activate(user_id: int, payment_id: str):
    """
    Тянет платёж из ЮKassa, синхронизирует payments.
    Если платёж успешен — пытается атомарно пометить его applied_at.
    Продлевает подписку ТОЛЬКО если пометка прошла впервые (идемпотентность).
    """
    p = await get_payment(payment_id)

    # 1) Синхронизируем запись платежа у себя
    amount_int = int(round(float(p.amount.value) * 100))
    await upsert_payment_status(
        user_id, payment_id, amount_int, p.amount.currency, p.status,
        raw_text=p.json(), confirmation_url=_get_confirmation_url(p)
    )

    # 2) Ветвление по статусу
    if p.status == "succeeded":
        # 2.1) idempotency: применяем платёж только один раз
        first_time = await mark_payment_applied(payment_id)
        if not first_time:
            # уже применяли раньше — ничего не продлеваем, но сообщаем успех
            return "succeeded"

        # 2.2) сохраним ИД способа оплаты (если он сохранён)
        pm_id = None
        try:
            if p.payment_method and getattr(p.payment_method, "saved", False):
                pm_id = p.payment_method.id
        except Exception:
            pm_id = None

        # 2.3) посчитаем корректные даты продления
        sub = await get_subscription(user_id)
        old_cpe = sub[3] if sub else None
        now = datetime.now(timezone.utc)
        new_cpe, next_charge_at = _calc_renewal_dates(old_cpe, now)

        # 2.4) продлеваем
        await upsert_subscription(
            user_id,
            status="active",
            payment_method_id=pm_id or (sub[2] if sub else None),
            current_period_end=new_cpe,
            next_charge_at=next_charge_at,
            amount=amount_int,
            currency=p.amount.currency
        )
        await cancel_other_pendings(user_id, keep_payment_id=payment_id) 
        return "succeeded"

    if p.status in ("pending", "waiting_for_capture"):
        return "pending"

    # canceled / failed / прочее
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
    # нормализуем к UTC-aware
    if isinstance(cpe, str):
        try:
            cpe_dt = datetime.fromisoformat(cpe.replace("Z", "+00:00"))
        except Exception:
            return False
    else:
        cpe_dt = cpe

    if cpe_dt is None:
        return False
    # если без tzinfo — считаем это UTC
    if cpe_dt.tzinfo is None:
        cpe_dt = cpe_dt.replace(tzinfo=timezone.utc)
    else:
        cpe_dt = cpe_dt.astimezone(timezone.utc)

    return status in ("active", "cancelled") and cpe_dt > datetime.now(timezone.utc)


async def start_or_resume_checkout(user_id: int, email: str | None):
    """
    Если есть pending — вернём ссылку на оплату для существующего платежа (из API или из БД).
    Если нет — создадим новый платеж.
    """
    last_pending = await get_last_pending_payment_id(user_id)
    if last_pending:
        p = await get_payment(last_pending)
        if p and p.status in ("pending", "waiting_for_capture"):
            url = _get_confirmation_url(p) or await get_payment_confirmation_url(last_pending)
            if url:
                return last_pending, url

    payment_id, url = await create_checkout_payment(user_id, email)
    await upsert_payment_status(user_id, payment_id, 0, "RUB", "pending", raw_text="{}", confirmation_url=url)
    return payment_id, url

# ---------- АВТОСПИСАНИЯ ----------

async def charge_recurring(user_id: int):
    """
    Пытается списать подписку по payment_method_id, если пришло время.
    Возвращает 'succeeded' | 'pending' | 'failed' | 'skipped'.
    """
    sub = await get_subscription(user_id)
    if not sub:
        return "skipped"

    status, pmid, cpe, nca = sub[1], sub[2], sub[3], sub[4]
    now = datetime.now(timezone.utc)

    # Списываем только если подписка активна и есть сохранённый способ оплаты
    if status != "active" or not pmid:
        return "skipped"

    # Нужен email для чека
    sub_email = _extract_email_from_subscription_row(sub)
    if not sub_email:
        # нет e-mail — корректнее не пытаться списывать (иначе SDK упадёт на _make_receipt)
        return "skipped"

    # нормализуем next_charge_at к UTC-aware
    if isinstance(nca, str):
        try:
            nca = datetime.fromisoformat(nca.replace("Z", "+00:00"))
        except Exception:
            nca = None
    if nca and nca.tzinfo is None:
        nca = nca.replace(tzinfo=timezone.utc)
    elif nca:
        nca = nca.astimezone(timezone.utc)

    if not nca or nca > now:
        return "skipped"

    # Не плодим новые pending, если уже есть
    pending = await get_last_pending_payment_id(user_id)
    if pending:
        p = await get_payment(pending)
        if p and p.status in ("pending", "waiting_for_capture"):
            return "pending"

    # Создаём рекуррентный платёж (передаём email!)
    payment = await create_recurring_payment(
        payment_method_id=pmid,
        user_id=user_id,
        email=sub_email,
        description="Продление подписки на 1 месяц"
    )

    amount_int = int(round(float(payment.amount.value) * 100))
    await upsert_payment_status(
        user_id, payment.id, amount_int, payment.amount.currency, payment.status, raw_text=payment.json()
    )

    if payment.status == "succeeded":
        # ИДЕМПОТЕНТНОСТЬ: применяем платёж только один раз на все гонки (вебхук/проверка)
        first_time = await mark_payment_applied(payment.id)
        if not first_time:
            # этот платёж уже применяли — просто сообщаем успех, не продлеваем ещё раз
            return "succeeded"

        # продлеваем на месяц (от cpe, если он в будущем; иначе от now)
        new_cpe, next_charge_at = _calc_renewal_dates(cpe, now)
        await upsert_subscription(
            user_id,
            status="active",
            current_period_end=new_cpe,
            next_charge_at=next_charge_at,
            amount=amount_int,
            currency=payment.amount.currency
        )

        # удаляем прочие "висящие" pending этого пользователя
        _ = await cancel_other_pendings(user_id, keep_payment_id=payment.id) 
        return "succeeded"


    if payment.status in ("pending", "waiting_for_capture"):
        # ждём вебхук/проверку
        return "pending"

    # failed: аккуратно назначим следующую попытку до конца периода,
    # чтобы не молотить каждую минуту
    cpe_dt = None
    if cpe:
        try:
            cpe_dt = datetime.fromisoformat(cpe.replace("Z", "+00:00")) if isinstance(cpe, str) else cpe
        except Exception:
            cpe_dt = None
        if cpe_dt and cpe_dt.tzinfo is None:
            cpe_dt = cpe_dt.replace(tzinfo=timezone.utc)
        elif cpe_dt:
            cpe_dt = cpe_dt.astimezone(timezone.utc)

    retry_at = min(cpe_dt, now + timedelta(hours=12)) if cpe_dt else (now + timedelta(hours=12))
    await upsert_subscription(user_id, next_charge_at=retry_at)
    return "failed"



async def charge_due_subscriptions():
    """
    Находит подписки, которым пора списать, и вызывает charge_recurring по каждой.
    Фильтр: status='active', payment_method_id NOT NULL, next_charge_at <= now.
    """
    from db import list_due_subscriptions
    now_dt = datetime.now(timezone.utc)
    due = await list_due_subscriptions(now_dt)
    results = {"succeeded": 0, "pending": 0, "failed": 0, "skipped": 0}
    for user_id in due:
        res = await charge_recurring(user_id)
        results[res] = results.get(res, 0) + 1
    return results