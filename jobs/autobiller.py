import asyncio
import logging
from billing.service import charge_due_subscriptions

log = logging.getLogger(__name__)

# reccurent payments, checking subscriptions table if next_charge_at is already in past
async def autobiller_loop(interval_sec: int, notifier=None) -> None:
    while True:
        try:
            res = await charge_due_subscriptions(notifier=notifier)
            log.info("autobiller: charged=%s", getattr(res, "count", res))
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("autobiller error")
        await asyncio.sleep(interval_sec)
