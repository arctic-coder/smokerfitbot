# tests/test_recurring_retries.py
import asyncio
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
import types
import billing.service as svc


def make_sub(active=True, pmid="pm_123", plan="month", email="u@test.com",
             cpe=None, nca=None, retry_attempts=0):
    now = datetime.now(timezone.utc)
    cpe = cpe or (now + timedelta(days=5))
    nca = nca or (cpe - timedelta(days=1))
    # (user_id, status, payment_method_id, current_period_end, next_charge_at,
    #  amount, currency, email, created_at, updated_at, plan, retry_attempts)
    return (
        42, "active" if active else "cancelled", pmid,
        cpe, nca,
        39900, "RUB", email,
        now, now,
        plan,
        retry_attempts,
    )


class TestRecurringRetries(unittest.TestCase):
    def test_failed_retries_and_cancel(self):
        async def run():
            now = datetime.now(timezone.utc)

            # 1-я неудача (retry_attempts=0): будет +1 день и попытка станет 1
            sub1 = make_sub(nca=now - timedelta(seconds=1), retry_attempts=0)
            notifier = AsyncMock()
            with patch('billing.service.get_subscription', new=AsyncMock(return_value=sub1)), \
                 patch('billing.service.get_last_pending_payment_id', new=AsyncMock(return_value=None)), \
                 patch('billing.service.create_recurring_payment', new=AsyncMock(return_value=types.SimpleNamespace(
                     id='p1', status='failed', amount=types.SimpleNamespace(value='399.00', currency='RUB'),
                     json=lambda: '{}'
                 ))), \
                 patch('billing.service.mark_payment_applied', new=AsyncMock(return_value=True)), \
                 patch('billing.service.upsert_payment_status', new=AsyncMock()), \
                 patch('billing.service.cancel_other_pendings', new=AsyncMock()), \
                 patch('billing.service.upsert_subscription', new=AsyncMock()) as m_upsert:
                res1 = await svc.charge_recurring(42, notifier=notifier)
                self.assertEqual(res1, 'failed')
                notifier.assert_any_await(42, 'precharge', {'plan': 'month'})
                notifier.assert_any_await(42, 'charged_failed', {'plan': 'month', 'attempt': 1})
                args = m_upsert.call_args.kwargs
                self.assertEqual(args['retry_attempts'], 1)
                self.assertAlmostEqual((args['next_charge_at'] - sub1[4]).total_seconds(), 24 * 3600, delta=5)

            # 2-я неудача: retry_attempts 1 -> 2 (без precharge)
            # ВАЖНО: nca должно быть due (<= now), иначе сервис вернёт "skipped"
            sub2 = make_sub(nca=now - timedelta(seconds=1), retry_attempts=1)
            notifier.reset_mock()
            with patch('billing.service.get_subscription', new=AsyncMock(return_value=sub2)), \
                 patch('billing.service.get_last_pending_payment_id', new=AsyncMock(return_value=None)), \
                 patch('billing.service.create_recurring_payment', new=AsyncMock(return_value=types.SimpleNamespace(
                     id='p2', status='failed', amount=types.SimpleNamespace(value='399.00', currency='RUB'),
                     json=lambda: '{}'
                 ))), \
                 patch('billing.service.mark_payment_applied', new=AsyncMock(return_value=True)), \
                 patch('billing.service.upsert_payment_status', new=AsyncMock()), \
                 patch('billing.service.cancel_other_pendings', new=AsyncMock()), \
                 patch('billing.service.upsert_subscription', new=AsyncMock()) as m_upsert:
                res2 = await svc.charge_recurring(42, notifier=notifier)
                self.assertEqual(res2, 'failed')
                # не должно быть precharge на повторных попытках
                for c in notifier.await_args_list:
                    self.assertNotEqual(c.args[1], 'precharge')
                args = m_upsert.call_args.kwargs
                self.assertEqual(args['retry_attempts'], 2)

            # 3-я неудача: статус cancelled и остановка ретраев
            # Тоже должно быть due
            sub3 = make_sub(nca=now - timedelta(seconds=1), retry_attempts=2)
            notifier.reset_mock()
            with patch('billing.service.get_subscription', new=AsyncMock(return_value=sub3)), \
                 patch('billing.service.get_last_pending_payment_id', new=AsyncMock(return_value=None)), \
                 patch('billing.service.create_recurring_payment', new=AsyncMock(return_value=types.SimpleNamespace(
                     id='p3', status='failed', amount=types.SimpleNamespace(value='399.00', currency='RUB'),
                     json=lambda: '{}'
                 ))), \
                 patch('billing.service.mark_payment_applied', new=AsyncMock(return_value=True)), \
                 patch('billing.service.upsert_payment_status', new=AsyncMock()), \
                 patch('billing.service.cancel_other_pendings', new=AsyncMock()), \
                 patch('billing.service.upsert_subscription', new=AsyncMock()) as m_upsert:
                res3 = await svc.charge_recurring(42, notifier=notifier)
                self.assertEqual(res3, 'failed')
                args = m_upsert.call_args.kwargs
                self.assertIsNone(args['next_charge_at'])
                self.assertEqual(args['retry_attempts'], 2)  # не растёт дальше
                self.assertEqual(args['status'], 'cancelled')
                notifier.assert_any_await(42, 'charged_failed', {'plan': 'month', 'attempt': 3})

        asyncio.run(run())

    def test_success_resets_retry_and_notifies(self):
        async def run():
            now = datetime.now(timezone.utc)
            sub = make_sub(nca=now - timedelta(seconds=1), retry_attempts=1, plan='year')
            notifier = AsyncMock()
            with patch('billing.service.get_subscription', new=AsyncMock(return_value=sub)), \
                 patch('billing.service.get_last_pending_payment_id', new=AsyncMock(return_value=None)), \
                 patch('billing.service.create_recurring_payment', new=AsyncMock(return_value=types.SimpleNamespace(
                     id='p_ok', status='succeeded', amount=types.SimpleNamespace(value='2990.00', currency='RUB'),
                     json=lambda: '{}'
                 ))), \
                 patch('billing.service.mark_payment_applied', new=AsyncMock(return_value=True)), \
                 patch('billing.service.upsert_payment_status', new=AsyncMock()), \
                 patch('billing.service.cancel_other_pendings', new=AsyncMock()), \
                 patch('billing.service.upsert_subscription', new=AsyncMock()) as m_upsert:
                res = await svc.charge_recurring(42, notifier=notifier)
                self.assertEqual(res, 'succeeded')
                notifier.assert_any_await(42, 'charged_success', {'plan': 'year'})
                args = m_upsert.call_args.kwargs
                self.assertEqual(args['retry_attempts'], 0)
                self.assertGreater(args['next_charge_at'], now)

        asyncio.run(run())


if __name__ == '__main__':
    unittest.main()
