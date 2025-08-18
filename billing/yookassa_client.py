import os
import uuid
from yookassa import Configuration, Payment

SUBSCRIPTION_PRICE = int(os.getenv("SUBSCRIPTION_PRICE", "29900"))
SUBSCRIPTION_CURRENCY = os.getenv("SUBSCRIPTION_CURRENCY", "RUB")
RETURN_URL = os.getenv("RETURN_URL", "https://t.me/")

# Фискальные настройки 
VAT_CODE = int(os.getenv("YOOKASSA_VAT_CODE", "1"))         
DEFAULT_CUSTOMER_EMAIL = os.getenv("YOOKASSA_DEFAULT_CUSTOMER_EMAIL", "test@example.com")

def _ensure_config():
    # вызывать перед каждым запросом, чтобы точно подхватить env
    shop_id = os.getenv("YOOKASSA_SHOP_ID")
    secret = os.getenv("YOOKASSA_SECRET_KEY")
    if not shop_id or not secret:
        raise RuntimeError("YOOKASSA_SHOP_ID / YOOKASSA_SECRET_KEY are not set")
    Configuration.account_id = shop_id
    Configuration.secret_key = secret

def _make_receipt(email: str | None, phone: str | None, amount_value: str):
    # customer обязателен, если включена фискализация
    customer = {}
    if email:
        customer = {"email": email}
    elif phone:
        customer = {"phone": phone}
    else:
        # для теста можно подставить дефолтный email
        customer = {"email": DEFAULT_CUSTOMER_EMAIL}

    receipt = {
        "customer": customer,
        "items": [{
            "description": "Подписка на тренировки (1 месяц)",
            "quantity": "1.00",  
            "amount": {"value": amount_value, "currency": SUBSCRIPTION_CURRENCY},
            "vat_code": VAT_CODE
        }]
    }
    return receipt

def create_checkout_payment(user_id: int, email: str | None, phone: str | None, description: str = "Подписка на тренировки"):
    _ensure_config()

    amount_value = "{:.2f}".format(SUBSCRIPTION_PRICE / 100)
    payload = {
        "amount": {"value": amount_value, "currency": SUBSCRIPTION_CURRENCY},
        "confirmation": {"type": "redirect", "return_url": RETURN_URL},
        "capture": True,
        "save_payment_method": True,
        "description": description,
        "metadata": {"user_id": str(user_id)},
        "receipt": _make_receipt(email, phone, amount_value)
    }

    idempotence_key = str(uuid.uuid4())
    payment = Payment.create(payload, idempotence_key)
    return payment.id, payment.confirmation.confirmation_url

def get_payment(payment_id: str):
    _ensure_config()
    return Payment.find_one(payment_id)

