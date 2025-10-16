# tests/test_autobilling.py
import asyncio
import unittest
from unittest.mock import AsyncMock, patch
import billing.service as svc

class TestAutoBilling(unittest.TestCase):
    def test_no_due_subscriptions(self):
        async def run():
            with patch('db.list_due_subscriptions', new=AsyncMock(return_value=[])) as m_list_due, \
                 patch('billing.service.charge_recurring', new=AsyncMock()) as m_charge_recurring:
                result = await svc.charge_due_subscriptions()  # notifier по умолчанию None
                self.assertEqual(result, {"succeeded": 0, "pending": 0, "failed": 0, "skipped": 0})
                m_charge_recurring.assert_not_awaited()
                m_list_due.assert_awaited_once()
        asyncio.run(run())

    def test_due_subscriptions_various_results(self):
        async def run():
            due_users = [101, 202, 303, 404]
            outcomes = {101: "succeeded", 202: "pending", 303: "failed", 404: "skipped"}

            async def fake_charge(user_id: int, notifier=None):
                return outcomes[user_id]

            with patch('db.list_due_subscriptions', new=AsyncMock(return_value=due_users)) as m_list_due, \
                 patch('billing.service.charge_recurring', new=AsyncMock(side_effect=fake_charge)) as m_charge_recurring:
                result = await svc.charge_due_subscriptions()
                expected = {"succeeded": 0, "pending": 0, "failed": 0, "skipped": 0}
                for o in outcomes.values():
                    expected[o] += 1
                self.assertEqual(result, expected)
                m_list_due.assert_awaited_once()
                self.assertEqual(m_charge_recurring.await_count, len(due_users))
        asyncio.run(run())

if __name__ == '__main__':
    unittest.main()
