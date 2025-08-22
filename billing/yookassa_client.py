import asyncio
import os, uuid
from yookassa import Configuration, Payment, Webhook
from requests.exceptions import Timeout, ConnectionError, RequestException

SUBSCRIPTION_PRICE = int(os.getenv("SUBSCRIPTION_PRICE", "39900"))
SUBSCRIPTION_CURRENCY = os.getenv("SUBSCRIPTION_CURRENCY", "RUB")
RETURN_URL = os.getenv("RETURN_URL", "https://t.me/")

# Фискальные настройки 
VAT_CODE = int(os.getenv("YOOKASSA_VAT_CODE", "1"))         
DEFAULT_CUSTOMER_EMAIL = os.getenv("YOOKASSA_DEFAULT_CUSTOMER_EMAIL", "test@example.com")

SUBSCRIPTION_TITLE = os.getenv("SUBSCRIPTION_TITLE", "Подписка «Физкультура курильщика» (1 месяц)")

class YookassaNetworkError(Exception):
    pass

async def _payment_create_async(payload: dict, idem: str):
    try:
        return await asyncio.to_thread(Payment.create, payload, idem)
    except Timeout:
        raise YookassaNetworkError("ЮKassa: время ожидания истекло")
    except ConnectionError:
        raise YookassaNetworkError("ЮKassa: нет соединения с ЮKassa")
    except RequestException:
        raise YookassaNetworkError("Сервис ЮKassa временно недоступен")

async def _payment_find_async(payment_id: str):
    try:
        return await asyncio.to_thread(Payment.find_one, payment_id)
    except Timeout:
        raise YookassaNetworkError("ЮKassa: время ожидания истекло")
    except ConnectionError:
        raise YookassaNetworkError("ЮKassa: нет соединения с ЮKassa")
    except RequestException:
        raise YookassaNetworkError("Сервис ЮKassa временно недоступен")

async def _payment_cancel_async(payment_id: str):
    try:
        return await asyncio.to_thread(Payment.cancel, payment_id)
    except Timeout:
        raise YookassaNetworkError("ЮKassa: время ожидания истекло")
    except ConnectionError:
        raise YookassaNetworkError("ЮKassa: нет соединения с ЮKassa")
    except RequestException:
        raise YookassaNetworkError("Сервис ЮKassa временно недоступен")


def _ensure_config():
    # вызывать перед каждым запросом, чтобы точно подхватить env
    shop_id = os.getenv("YOOKASSA_SHOP_ID")
    secret = os.getenv("YOOKASSA_SECRET_KEY")
    if not shop_id or not secret:
        raise RuntimeError("YOOKASSA_SHOP_ID / YOOKASSA_SECRET_KEY are not set")
    Configuration.account_id = shop_id
    Configuration.secret_key = secret

def _make_receipt(email: str | None, amount_value: str):
    if not email:
        raise ValueError("Email обязателен для отправки чека")
    customer = {"email": email}

    receipt = {
        "customer": customer,
        "items": [{
            "description": SUBSCRIPTION_TITLE,
            "quantity": "1.00",  
            "amount": {"value": amount_value, "currency": SUBSCRIPTION_CURRENCY},
            "vat_code": VAT_CODE
        }]
    }
    return receipt

async def create_checkout_payment(user_id: int, email: str | None, description: str = SUBSCRIPTION_TITLE):

    _ensure_config()

    amount_value = "{:.2f}".format(SUBSCRIPTION_PRICE / 100)
    payload = {
        "amount": {"value": amount_value, "currency": SUBSCRIPTION_CURRENCY},
        "confirmation": {"type": "redirect", "return_url": RETURN_URL},
        "capture": True,
        "save_payment_method": True,
        "description": description,
        "metadata": {"user_id": str(user_id), "origin": "initial"},
        "receipt": _make_receipt(email, amount_value)
    }
    payment = await _payment_create_async(payload, str(uuid.uuid4()))
    return payment.id, payment.confirmation.confirmation_url

async def create_recurring_payment(payment_method_id: str, user_id: int, email: str | None, description: str = f"Продление: {SUBSCRIPTION_TITLE}"):

    """
    Создаёт рекуррентный платёж по сохранённому способу оплаты (без редиректа).
    """
    _ensure_config()
    amount_value = "{:.2f}".format(SUBSCRIPTION_PRICE / 100)
    payload = {
        "amount": {"value": amount_value, "currency": SUBSCRIPTION_CURRENCY},
        "payment_method_id": payment_method_id,
        "capture": True,
        "description": description,
        "metadata": {"user_id": str(user_id), "origin": "recurring"},
        "receipt": _make_receipt(email=email, amount_value=amount_value),
    }
    return await _payment_create_async(payload, str(uuid.uuid4()))

async def get_payment(payment_id: str):
    _ensure_config()
    return await _payment_find_async(payment_id)
