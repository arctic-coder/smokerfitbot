# handlers/__init__.py
from aiogram import Dispatcher
from .common import register_common_handlers
from .form import register_form_handlers
from .subscription import register_subscription_handlers

def register_handlers(dp: Dispatcher) -> None:
    register_common_handlers(dp)
    register_form_handlers(dp)
    register_subscription_handlers(dp)
