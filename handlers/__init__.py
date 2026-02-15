# handlers/__init__.py
from aiogram import Router

from .common import common_router
from .form import form_router
from .subscription import subscription_router


def get_main_router() -> Router:
    router = Router()
    router.include_router(common_router)
    router.include_router(form_router)
    router.include_router(subscription_router)
    return router
