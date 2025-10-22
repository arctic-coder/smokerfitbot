import logging
import json
from aiohttp import web
from billing.service import check_and_activate
from db import get_user_id_by_payment_id

log = logging.getLogger(__name__)
# currently only succeed webhooks. NEED TO BE CONFIGURED IN YOOKASSA SHOP
async def yookassa_webhook(request: web.Request) -> web.Response:
    try:
        data = await request.json()
        # todo add validation for JSON
    except Exception:
        return web.Response(status=400, text="bad json")
    
    # log webhook
    try:
        evt = (data or {}).get("event")
        obj = (data or {}).get("object") or {}
        log.info("yookassa_webhook: event=%s id=%s status=%s", evt, obj.get("id"), obj.get("status"))
        log.debug("yookassa_webhook: body=%s", json.dumps(data, ensure_ascii=False))
    except Exception:
        log.exception("yookassa_webhook: failed to log incoming payload")

    # activating subscription for this payment_id
    payment = (data or {}).get("object") or {}
    payment_id = payment.get("id")
    if payment_id:
        try:
            uid = await get_user_id_by_payment_id(payment_id)
            if uid:
                await check_and_activate(uid, payment_id)
        except Exception as e:
            log.exception("yookassa_webhook failed: %s", e)
            # возвращаем 200/ok, чтобы YooKassa не спамила ретраями
    return web.Response(text="ok")