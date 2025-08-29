# yookassa_client.py
import asyncio
import os, uuid
import json, copy, re, logging
from requests.exceptions import Timeout, ConnectionError, RequestException

from yookassa import Configuration, Payment, Webhook
from yookassa.domain.exceptions import ApiError

# ==== Константы из окружения ====
SUBSCRIPTION_PRICE = int(os.getenv("SUBSCRIPTION_PRICE", "39900"))
SUBSCRIPTION_CURRENCY = os.getenv("SUBSCRIPTION_CURRENCY", "RUB")
RETURN_URL = os.getenv("RETURN_URL", "https://t.me/")
SUBSCRIPTION_TITLE = os.getenv("SUBSCRIPTION_TITLE", "Подписка «Физкультура курильщика» (1 месяц)")

# Фискальные настройки
VAT_CODE = int(os.getenv("YOOKASSA_VAT_CODE", "1"))
DEFAULT_CUSTOMER_EMAIL = os.getenv("YOOKASSA_DEFAULT_CUSTOMER_EMAIL", "test@example.com")

# Логгер этого модуля
log = logging.getLogger("billing.yookassa")


# ==== Исключение сети ====
class YookassaNetworkError(Exception):
    pass


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
def _make_receipt(email: str | None, amount_value: str):
    """Минимальный чек: 1 позиция, 1 шт., с НДС VAT_CODE."""
    if not email:
        raise ValueError("Email обязателен для отправки чека")
    customer = {"email": email}
    receipt = {
        "customer": customer,
        "items": [{
            "description": SUBSCRIPTION_TITLE,
            "quantity": "1.00",
            "amount": {"value": amount_value, "currency": SUBSCRIPTION_CURRENCY},
            "vat_code": VAT_CODE,
        }]
    }
    return receipt


# ==== НИЗКОУРОВНЕВЫЕ ВЫЗОВЫ API С ЛОГАМИ ====
async def _payment_create_async(payload: dict, idem: str):
    """POST /v3/payments с логированием запроса/ответа/ошибок."""
    _ensure_config()
    # DEBUG: исходящий payload (замаскирован)
    log.debug("YK request Payment.create: idem=%s payload=%s",
              idem, json.dumps(_redact_payload(payload), ensure_ascii=False))
    try:
        p = await asyncio.to_thread(Payment.create, payload, idem)
        # INFO: коротко
        status = getattr(p, "status", None)
        pid = getattr(p, "id", None)
        conf_obj = getattr(p, "confirmation", None)
        conf_url = getattr(conf_obj, "confirmation_url", None) if conf_obj else None
        log.info("YK response Payment.create: id=%s status=%s", pid, status)
        # DEBUG: полный ответ
        try:
            log.debug("YK response Payment.create: confirmation_url=%s body=%s",
                      conf_url, p.json())
        except Exception:
            # На всякий — сериализация asdict
            log.debug("YK response Payment.create: confirmation_url=%s (json() failed)", conf_url)
        return p

    except ApiError as e:
        # Ошибка со стороны API (403/401/400/422 и т.д.)
        http = getattr(e, "http_code", None)
        req_id = getattr(e, "request_id", None)
        code = getattr(e, "code", e.__class__.__name__)
        msg = getattr(e, "message", str(e))
        params = getattr(e, "params", None)
        log.error(
            "YK API error Payment.create: http=%s request_id=%s code=%s message=%s params=%s idem=%s payload=%s",
            http, req_id, code, msg, params, idem, json.dumps(_redact_payload(payload), ensure_ascii=False)
        )
        raise

    except Timeout:
        log.error("YK network timeout on Payment.create idem=%s", idem)
        raise YookassaNetworkError("ЮKassa: время ожидания истекло")
    except ConnectionError:
        log.error("YK connection error on Payment.create idem=%s", idem)
        raise YookassaNetworkError("ЮKassa: нет соединения с ЮKassa")
    except RequestException:
        log.error("YK generic network error on Payment.create idem=%s", idem)
        raise YookassaNetworkError("Сервис ЮKassa временно недоступен")

async def _payment_find_async(payment_id: str):
    """GET /v3/payments/{id} с логированием."""
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
        log.error(
            "YK API error Payment.find_one: http=%s request_id=%s code=%s message=%s params=%s payment_id=%s",
            http, req_id, code, msg, params, payment_id
        )
        raise
    except Timeout:
        log.error("YK network timeout on Payment.find_one id=%s", payment_id)
        raise YookassaNetworkError("ЮKassa: время ожидания истекло")
    except ConnectionError:
        log.error("YK connection error on Payment.find_one id=%s", payment_id)
        raise YookassaNetworkError("ЮKassa: нет соединения с ЮKassa")
    except RequestException:
        log.error("YK generic network error on Payment.find_one id=%s", payment_id)
        raise YookassaNetworkError("Сервис ЮKassa временно недоступен")

async def _payment_cancel_async(payment_id: str):
    """POST /v3/payments/{id}/cancel с логированием."""
    _ensure_config()
    log.debug("YK request Payment.cancel: id=%s", payment_id)
    try:
        p = await asyncio.to_thread(Payment.cancel, payment_id)
        log.info("YK response Payment.cancel: id=%s status=%s", getattr(p, "id", None), getattr(p, "status", None))
        try:
            log.debug("YK response Payment.cancel: body=%s", p.json())
        except Exception:
            pass
        return p
    except ApiError as e:
        http = getattr(e, "http_code", None)
        req_id = getattr(e, "request_id", None)
        code = getattr(e, "code", e.__class__.__name__)
        msg = getattr(e, "message", str(e))
        params = getattr(e, "params", None)
        log.error(
            "YK API error Payment.cancel: http=%s request_id=%s code=%s message=%s params=%s payment_id=%s",
            http, req_id, code, msg, params, payment_id
        )
        raise
    except Timeout:
        log.error("YK network timeout on Payment.cancel id=%s", payment_id)
        raise YookassaNetworkError("ЮKassa: время ожидания истекло")
    except ConnectionError:
        log.error("YK connection error on Payment.cancel id=%s", payment_id)
        raise YookassaNetworkError("ЮKassa: нет соединения с ЮKassa")
    except RequestException:
        log.error("YK generic network error on Payment.cancel id=%s", payment_id)
        raise YookassaNetworkError("Сервис ЮKassa временно недоступен")


# ==== ВЫСОКОУРОВНЕВЫЕ ОБЁРТКИ ДЛЯ ПРИЛОЖЕНИЯ ====
async def create_checkout_payment(user_id: int, email: str | None, description: str = SUBSCRIPTION_TITLE):
    """
    Создаёт платёж с редиректом (initial checkout) и сохранением способа оплаты.
    Возвращает (payment_id, confirmation_url)
    """
    amount_value = "{:.2f}".format(SUBSCRIPTION_PRICE / 100)
    payload = {
        "amount": {"value": amount_value, "currency": SUBSCRIPTION_CURRENCY},
        "confirmation": {"type": "redirect", "return_url": RETURN_URL},
        "capture": True,
        "save_payment_method": True,
        "description": description,
        "metadata": {"user_id": str(user_id), "origin": "initial"},
        "receipt": _make_receipt(email, amount_value),
    }
    idem = str(uuid.uuid4())
    p = await _payment_create_async(payload, idem)
    conf_obj = getattr(p, "confirmation", None)
    url = getattr(conf_obj, "confirmation_url", None) if conf_obj else None
    return p.id, url

async def create_recurring_payment(payment_method_id: str, user_id: int, email: str | None,
                                   description: str = f"Продление: {SUBSCRIPTION_TITLE}"):
    """
    Рекуррент по сохранённому способу оплаты (без редиректа).
    Возвращает объект Payment.
    """
    amount_value = "{:.2f}".format(SUBSCRIPTION_PRICE / 100)
    payload = {
        "amount": {"value": amount_value, "currency": SUBSCRIPTION_CURRENCY},
        "payment_method_id": payment_method_id,
        "capture": True,
        "description": description,
        "metadata": {"user_id": str(user_id), "origin": "recurring"},
        "receipt": _make_receipt(email=email, amount_value=amount_value),
    }
    idem = str(uuid.uuid4())
    return await _payment_create_async(payload, idem)

async def get_payment(payment_id: str):
    """Обёртка для поиска платежа по id."""
    return await _payment_find_async(payment_id)
