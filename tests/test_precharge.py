# tests/test_precharge.py
import asyncio
import unittest
from unittest.mock import AsyncMock, patch
import billing.service as svc

class TestPrecharge(unittest.TestCase):
    def test_precharge_sent_once_and_marked(self):
        async def run():
            notifier = AsyncMock()
            with patch('billing.service.list_precharge_subscriptions', new=AsyncMock(return_value=[42])), \
                 patch('billing.service.get_subscription', new=AsyncMock(return_value=(
                     42, "active", "pm_123", None, None,
                     39900, "RUB", "u@test.com", None, None,
                     "month", 0, False
                 ))), \
                 patch('billing.service.mark_precharge_sent', new=AsyncMock()) as m_mark:
                sent = await svc.send_precharge_notifications(notifier=notifier)
                self.assertEqual(sent, 1)
                notifier.assert_awaited_once_with(42, "precharge", {"plan": "month"})
                m_mark.assert_awaited_once_with(42)
        asyncio.run(run())

    def test_precharge_skipped_if_retry_or_already_sent(self):
        async def run():
            notifier = AsyncMock()

            # Уже отправляли ранее
            with patch('billing.service.list_precharge_subscriptions', new=AsyncMock(return_value=[42])), \
                 patch('billing.service.get_subscription', new=AsyncMock(return_value=(
                     42, "active", "pm_123", None, None,
                     39900, "RUB", "u@test.com", None, None,
                     "month", 0, True
                 ))), \
                 patch('billing.service.mark_precharge_sent', new=AsyncMock()) as m_mark:
                sent = await svc.send_precharge_notifications(notifier=notifier)
                self.assertEqual(sent, 0)
                notifier.assert_not_awaited()
                m_mark.assert_not_awaited()

            # Это уже ретрай — не шлём precharge
            notifier.reset_mock()
            with patch('billing.service.list_precharge_subscriptions', new=AsyncMock(return_value=[42])), \
                 patch('billing.service.get_subscription', new=AsyncMock(return_value=(
                     42, "active", "pm_123", None, None,
                     39900, "RUB", "u@test.com", None, None,
                     "month", 1, False
                 ))), \
                 patch('billing.service.mark_precharge_sent', new=AsyncMock()) as m_mark:
                sent = await svc.send_precharge_notifications(notifier=notifier)
                self.assertEqual(sent, 0)
                notifier.assert_not_awaited()
                m_mark.assert_not_awaited()
        asyncio.run(run())

if __name__ == '__main__':
    unittest.main()
