from datetime import datetime, timedelta, timezone
from typing import Awaitable, Callable, Optional, Dict, Any
from db import (
    upsert_subscription, upsert_payment_status, get_last_pending_payment_id,
    get_payment_confirmation_url, get_subscription, mark_payment_applied, cancel_other_pendings,
    list_precharge_subscriptions, mark_precharge_sent
)
from billing.yookassa_client import amount_for, create_checkout_payment, get_payment, create_recurring_payment
import logging
log = logging.getLogger("billing.service")
# Async-колбэк уведомлений: (user_id, kind, ctx) -> await None
Notifier = Optional[Callable[[int, str, Dict[str, Any]], Awaitable[None]]]

def _add_months(dt: datetime, n: int) -> datetime:
    cur = dt
    for _ in range(n):
        cur = _next_month(cur) 
    return cur

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


def _calc_renewal_dates(current_period_end, now_utc: datetime, months: int):
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
    new_cpe = _add_months(anchor, months)
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
        first_time = await mark_payment_applied(payment_id)
        if not first_time:
            return "succeeded"

        plan = None
        try:
            md = getattr(p, "metadata", None)
            plan = md.get("plan") if md else None
        except Exception:
            pass
        if plan not in ("month", "year"):
            plan = "month"

        sub = await get_subscription(user_id)
        old_cpe = sub[3] if sub else None
        now = datetime.now(timezone.utc)
        months = 12 if plan == "year" else 1
        new_cpe, next_charge_at = _calc_renewal_dates(old_cpe, now, months)

        await upsert_subscription(
            user_id,
            status="active",
            payment_method_id=(p.payment_method.id if getattr(getattr(p, "payment_method", None), "saved", False) else (sub[2] if sub else None)),
            current_period_end=new_cpe,
            next_charge_at=next_charge_at,
            retry_attempts=0,
            precharge_notified=False,
            amount=int(round(float(p.amount.value) * 100)),
            currency=p.amount.currency,
            plan=plan,
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


async def start_or_resume_checkout(
    user_id: int,
    email: str | None,
    plan: str,
    price_override_cents: int | None = None,
    promo_code: str | None = None,
    promo_title: str | None = None,
):
    last_pending_id = await get_last_pending_payment_id(user_id)
    if last_pending_id:
        p = await get_payment(last_pending_id)
        if p and p.status in ("pending", "waiting_for_capture"):
            md = getattr(p, "metadata", None)
            p_plan = (md.get("plan") if md else None) or "month"
            p_promo_code = (md.get("promo_code") if md else None) or None
            try:
                p_price = int(md.get("promo_price_cents")) if md and md.get("promo_price_cents") is not None else None
            except Exception:
                p_price = None
            desired_price = price_override_cents
            if p_price is None and getattr(p, "amount", None):
                try:
                    p_price = int(round(float(p.amount.value) * 100))
                except Exception:
                    p_price = None

            if p_plan == plan and (desired_price is None or p_price == desired_price) and (promo_code or None) == (p_promo_code or None):
                url = _get_confirmation_url(p) or await get_payment_confirmation_url(last_pending_id)
                if url:
                    return last_pending_id, url
            # если план отличается — не переиспользуем тот pending

    payment_id, url = await create_checkout_payment(
        user_id,
        email,
        plan,
        price_cents_override=price_override_cents,
        promo_code=promo_code,
        promo_title=promo_title,
    )
    fallback_amount = price_override_cents if price_override_cents is not None else amount_for(plan)[0]
    await upsert_payment_status(user_id, payment_id, fallback_amount, "RUB", "pending", raw_text="{}", confirmation_url=url)
    return payment_id, url

# ---------- АВТОСПИСАНИЯ ----------

async def charge_recurring(user_id: int, notifier: Notifier = None):
    """
    Пытается списать подписку по payment_method_id, если пришло время.
    Возвращает 'succeeded' | 'pending' | 'failed' | 'skipped'.
    """
    sub = await get_subscription(user_id)
    if not sub:
        return "skipped"

    status, pmid, cpe, nca = sub[1], sub[2], sub[3], sub[4]
    plan = (sub[10] if len(sub) > 10 else None) or "month"
    retry_attempts = (sub[11] if len(sub) > 11 else 0) or 0
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
    months = 12 if plan == "year" else 1
    payment = await create_recurring_payment(pmid, user_id, sub_email, plan)


    amount_int = int(round(float(payment.amount.value) * 100))
    await upsert_payment_status(
        user_id, payment.id, amount_int, payment.amount.currency, payment.status, raw_text=payment.json()
    )

    if payment.status == "succeeded":
        # ИДЕМПОТЕНТНОСТЬ: применяем платёж только один раз на все гонки (вебхук/проверка)
        first_time = await mark_payment_applied(payment.id)
        if not first_time:
            # этот платёж уже применяли — просто сообщаем успех, не продлеваем ещё раз
            if notifier is not None:
                try:
                    await notifier(user_id, "charged_success", {"plan": plan})
                except Exception:
                    log.exception("success notify failed for user_id=%s (idempotent)", user_id)
            return "succeeded"

        # продлеваем на месяц (от cpe, если он в будущем; иначе от now)
        new_cpe, next_charge_at = _calc_renewal_dates(cpe, now, months)
        await upsert_subscription(
            user_id,
            status="active",
            current_period_end=new_cpe,
            next_charge_at=next_charge_at,
            retry_attempts=0,
            precharge_notified=False,  # новый цикл — снова ждём precharge
            amount=int(round(float(payment.amount.value) * 100)),
            currency=payment.amount.currency,
            plan=plan,
        )

        # удаляем прочие "висящие" pending этого пользователя
        _ = await cancel_other_pendings(user_id, keep_payment_id=payment.id) 
        if notifier is not None:
            try:
                await notifier(user_id, "charged_success", {"plan": plan})
            except Exception:
                log.exception("success notify failed for user_id=%s", user_id)
        return "succeeded"

    if payment.status in ("pending", "waiting_for_capture"):
        # ждём вебхук/проверку
        return "pending"

    # failed: ретраи 1 раз в сутки, максимум до 3 попыток (0 + 2 ретрая)
    # следующая дата попытки — на +1 день от предыдущей (если nca известна), иначе от now
    # после 3-й неудачи прекращаем (next_charge_at=None)
    if retry_attempts >= 2:
        if notifier is not None:
            try:
                await notifier(user_id, "charged_failed_last", {"plan": plan, "attempt": retry_attempts + 1})
            except Exception:
                log.exception("failed notify failed for user_id=%s", user_id)
        # попытки исчерпаны: отключаем автопродление
        await upsert_subscription(
            user_id,
            status="cancelled",
            next_charge_at=None,
            retry_attempts=retry_attempts
        )
        return "failed"

    if notifier is not None:
            try:
                await notifier(user_id, "charged_failed", {"plan": plan, "attempt": retry_attempts + 1})
            except Exception:
                log.exception("failed notify failed for user_id=%s", user_id)

    base = nca if isinstance(nca, datetime) else now
    next_try = base + timedelta(days=1)
    await upsert_subscription(user_id, next_charge_at=next_try, retry_attempts=retry_attempts + 1)
    return "failed"

async def charge_due_subscriptions(notifier: Notifier = None):
    """
    Находит подписки, которым пора списать, и вызывает charge_recurring по каждой.
    Фильтр: status='active', payment_method_id NOT NULL, next_charge_at <= now.
    """
    from db import list_due_subscriptions
    now_dt = datetime.now(timezone.utc)
    due = await list_due_subscriptions(now_dt)
    results = {"succeeded": 0, "pending": 0, "failed": 0, "skipped": 0}
    for user_id in due:
        res = await charge_recurring(user_id, notifier=notifier)
        results[res] = results.get(res, 0) + 1
    return results

async def send_precharge_notifications(notifier: Notifier = None) -> int:
    """
    Разослать precharge, как только наступил порог (>= 24 часа до первой попытки).
    Идемпотентность обеспечивается флагом precharge_notified в БД.
    """
    if notifier is None:
        return 0
    user_ids = await list_precharge_subscriptions()
    sent = 0
    for uid in user_ids:
        sub = await get_subscription(uid)
        if not sub:
            continue
        plan = (sub[10] if len(sub) > 10 else None) or "month"
        retry_attempts = (sub[11] if len(sub) > 11 else 0) or 0
        pre_sent = (sub[12] if len(sub) > 12 else False) or False
        if retry_attempts != 0 or pre_sent:
            continue
        try:
            await notifier(uid, "precharge", {"plan": plan})
            await mark_precharge_sent(uid)
            sent += 1
        except Exception:
            log.exception("precharge notify failed user_id=%s", uid)
    return sent
