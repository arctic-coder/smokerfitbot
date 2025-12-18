# yookassa_client.py
import asyncio
import os, uuid
import json, copy, re, logging
from requests.exceptions import Timeout, ConnectionError, RequestException, HTTPError

from yookassa import Configuration, Payment, Webhook
from yookassa.domain.exceptions import ApiError

# ==== Константы из окружения ====
SUBSCRIPTION_PRICE_MONTH = int(os.getenv("SUBSCRIPTION_PRICE_MONTH", "39900"))
SUBSCRIPTION_PRICE_YEAR  = int(os.getenv("SUBSCRIPTION_PRICE_YEAR",  "299000"))
SUBSCRIPTION_TITLE_MONTH = "Подписка «Физкультура курильщика» (1 месяц)"
SUBSCRIPTION_TITLE_YEAR  = "Подписка «Физкультура курильщика» (1 год)"
SUBSCRIPTION_CURRENCY = os.getenv("SUBSCRIPTION_CURRENCY", "RUB")
RETURN_URL = os.getenv("RETURN_URL", "https://t.me/")

# Фискальные настройки
VAT_CODE = int(os.getenv("YOOKASSA_VAT_CODE", "1"))
DEFAULT_CUSTOMER_EMAIL = os.getenv("YOOKASSA_DEFAULT_CUSTOMER_EMAIL", "test@example.com")

# Логгер этого модуля
log = logging.getLogger("billing.yookassa")


# ==== Исключение сети ====
class YookassaNetworkError(Exception):
    pass

def _fmt(cents: int) -> str:
    return "{:.2f}".format(cents / 100)

def amount_for(plan: str, override_cents: int | None = None, title_override: str | None = None) -> tuple[int, str, str]:
    if plan == "year":
        cents, title = SUBSCRIPTION_PRICE_YEAR, SUBSCRIPTION_TITLE_YEAR
    else:
        cents, title = SUBSCRIPTION_PRICE_MONTH, SUBSCRIPTION_TITLE_MONTH
    if override_cents is not None:
        cents = int(override_cents)
    if title_override:
        title = title_override
    return cents, _fmt(cents), title

def _log_requests_error(prefix: str, exc: Exception):
    """
    Логирует статус, X-Request-Id и тело ответа, если исключение пришло из requests
    (HTTPError/RequestException) и в нём есть .response.
    """
    r = getattr(exc, "response", None)
    if r is not None:
        try:
            text = r.text  # тело ответа (JSON с description)
        except Exception:
            text = "<unreadable body>"
        req_id = r.headers.get("X-Request-Id") or r.headers.get("x-request-id")
        try:
            # не падаем на потенциальной бинарщине
            log.error("%s: http=%s request_id=%s body=%s", prefix, r.status_code, req_id, text)
        except Exception:
            log.error("%s: http=%s request_id=%s (body not logged)", prefix, r.status_code, req_id)
    else:
        log.error("%s: %r (no response attached)", prefix, exc)


# ==== Утилиты маскировки и конфигурации ====
def _mask_email(email: str | None) -> str | None:
    """user@example.com -> u***r@example.com"""
    if not email or "@" not in email:
        return email
    name, domain = email.split("@", 1)
    if len(name) <= 2:
        masked = "***"
    else:
        masked = f"{name[0]}***{name[-1]}"
    return f"{masked}@{domain}"

def _redact_payload(d: dict) -> dict:
    """Глубокая копия payload с маскировкой чувствительных полей."""
    red = copy.deepcopy(d)
    try:
        cust = (((red.get("receipt") or {}).get("customer")) or {})
        if "email" in cust:
            cust["email"] = _mask_email(cust["email"])
    except Exception:
        pass
    try:
        pmid = red.get("payment_method_id")
        if isinstance(pmid, str):
            red["payment_method_id"] = f"{pmid[:6]}***{pmid[-4:]}" if len(pmid) > 10 else "***"
    except Exception:
        pass
    return red

def _ensure_config():
    """Подтягивает креды из ENV перед каждым запросом."""
    shop_id = os.getenv("YOOKASSA_SHOP_ID")
    secret = os.getenv("YOOKASSA_SECRET_KEY")
    if not shop_id or not secret:
        raise RuntimeError("YOOKASSA_SHOP_ID / YOOKASSA_SECRET_KEY are not set")
    Configuration.account_id = shop_id
    Configuration.secret_key = secret


# ==== Сборка чека ====
def _make_receipt(email: str | None, amount_value: str, title: str):
    """Минимальный чек: 1 позиция, 1 шт., с НДС VAT_CODE."""
    if not email:
        raise ValueError("Email обязателен для отправки чека")
    customer = {"email": email}
    receipt = {
        "customer": customer,
        "items": [{
            "description": title,
            "quantity": "1.00",
            "amount": {"value": amount_value, "currency": SUBSCRIPTION_CURRENCY},
            "vat_code": VAT_CODE,
        }]
    }
    return receipt


# ==== НИЗКОУРОВНЕВЫЕ ВЫЗОВЫ API С ЛОГАМИ ====
async def _payment_create_async(payload: dict, idem: str):
    """POST /v3/payments с логированием запроса/ответа/ошибок (включая тело 4xx)."""
    _ensure_config()
    log.debug("YK request Payment.create: idem=%s payload=%s",
              idem, json.dumps(_redact_payload(payload), ensure_ascii=False))
    try:
        p = await asyncio.to_thread(Payment.create, payload, idem)
        status = getattr(p, "status", None)
        pid = getattr(p, "id", None)
        conf_obj = getattr(p, "confirmation", None)
        conf_url = getattr(conf_obj, "confirmation_url", None) if conf_obj else None
        log.info("YK response Payment.create: id=%s status=%s", pid, status)
        try:
            log.debug("YK response Payment.create: confirmation_url=%s body=%s", conf_url, p.json())
        except Exception:
            log.debug("YK response Payment.create: confirmation_url=%s (json() failed)", conf_url)
        return p

    except ApiError as e:
        http = getattr(e, "http_code", None)
        req_id = getattr(e, "request_id", None)
        code = getattr(e, "code", e.__class__.__name__)
        msg = getattr(e, "message", str(e))
        params = getattr(e, "params", None)
        log.error("YK API error Payment.create: http=%s request_id=%s code=%s message=%s params=%s idem=%s payload=%s",
                  http, req_id, code, msg, params, idem, json.dumps(_redact_payload(payload), ensure_ascii=False))
        raise

    except HTTPError as e:  # важно: до RequestException
        _log_requests_error("YK HTTP error Payment.create", e)
        raise

    except Timeout:
        log.error("YK network timeout on Payment.create idem=%s", idem)
        raise YookassaNetworkError("ЮKassa: время ожидания истекло")
    except ConnectionError:
        log.error("YK connection error on Payment.create idem=%s", idem)
        raise YookassaNetworkError("ЮKassa: нет соединения с ЮKassa")
    except RequestException as e:
        # сюда падают прочие ошибки requests (включая 4xx/5xx, если SDK не преобразовал в ApiError)
        _log_requests_error("YK generic network error on Payment.create", e)
        raise YookassaNetworkError("Сервис ЮKassa временно недоступен")


async def _payment_find_async(payment_id: str):
    """GET /v3/payments/{id} с логированием тела на ошибках."""
    _ensure_config()
    log.debug("YK request Payment.find_one: id=%s", payment_id)
    try:
        p = await asyncio.to_thread(Payment.find_one, payment_id)
        log.info("YK response Payment.find_one: id=%s status=%s", getattr(p, "id", None), getattr(p, "status", None))
        try:
            log.debug("YK response Payment.find_one: body=%s", p.json())
        except Exception:
            pass
        return p

    except ApiError as e:
        http = getattr(e, "http_code", None)
        req_id = getattr(e, "request_id", None)
        code = getattr(e, "code", e.__class__.__name__)
        msg = getattr(e, "message", str(e))
        params = getattr(e, "params", None)
        log.error("YK API error Payment.find_one: http=%s request_id=%s code=%s message=%s params=%s payment_id=%s",
                  http, req_id, code, msg, params, payment_id)
        raise
    except HTTPError as e:
        _log_requests_error("YK HTTP error Payment.find_one", e)
        raise
    except Timeout:
        log.error("YK network timeout on Payment.find_one id=%s", payment_id)
        raise YookassaNetworkError("ЮKassa: время ожидания истекло")
    except ConnectionError:
        log.error("YK connection error on Payment.find_one id=%s", payment_id)
        raise YookassaNetworkError("ЮKassa: нет соединения с ЮKassa")
    except RequestException as e:
        _log_requests_error("YK generic network error on Payment.find_one", e)
        raise YookassaNetworkError("Сервис ЮKassa временно недоступен")

# ==== ВЫСОКОУРОВНЕВЫЕ ОБЁРТКИ ДЛЯ ПРИЛОЖЕНИЯ ====
async def create_checkout_payment(
    user_id: int,
    email: str | None,
    plan: str,
    price_cents_override: int | None = None,
    promo_code: str | None = None,
    promo_title: str | None = None,
):
    """
    Создаёт платёж с редиректом (initial checkout) и сохранением способа оплаты.
    Возвращает (payment_id, confirmation_url)
    """
    cents, value, base_title = amount_for(plan, override_cents=price_cents_override)
    # Оставляем стандартное название плана и лишь помечаем, что оплата по промокоду
    desc_title = f"{base_title} (Промокод)" if promo_code else base_title
    payload = {
        "amount": {"value": value, "currency": SUBSCRIPTION_CURRENCY},
        "confirmation": {"type": "redirect", "return_url": RETURN_URL},
        "capture": True,
        "save_payment_method": True,
        "description": desc_title,
        "metadata": {
            "user_id": str(user_id),
            "origin": "initial",
            "plan": plan,
            "promo_code": promo_code,
            "promo_price_cents": cents if price_cents_override is not None else None,
            "promo_title": promo_title,
        },
        "receipt": _make_receipt(email, value, desc_title),
    }
    payload["metadata"] = {k: v for k, v in payload["metadata"].items() if v is not None}
    idem = str(uuid.uuid4())
    p = await _payment_create_async(payload, idem)
    conf_obj = getattr(p, "confirmation", None)
    url = getattr(conf_obj, "confirmation_url", None) if conf_obj else None
    return p.id, url

async def create_recurring_payment(payment_method_id: str, user_id: int, email: str | None, plan: str):
    """
    Рекуррент по сохранённому способу оплаты (без редиректа).
    Возвращает объект Payment.
    """
    cents, value, title = amount_for(plan)
    payload = {
        "amount": {"value": value, "currency": SUBSCRIPTION_CURRENCY},
        "payment_method_id": payment_method_id,
        "capture": True,
        "description": f"Продление: {title}",
        "metadata": {"user_id": str(user_id), "origin": "recurring", "plan": plan},
        "receipt": _make_receipt(email, value, title),
    }
    idem = str(uuid.uuid4())
    return await _payment_create_async(payload, idem)

async def get_payment(payment_id: str):
    """Обёртка для поиска платежа по id."""
    return await _payment_find_async(payment_id)
