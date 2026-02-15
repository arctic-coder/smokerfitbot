# tests/test_billing_service.py
from datetime import datetime, timedelta, timezone

from billing.service import _add_months, _calc_renewal_dates, _next_month, is_active


def test_is_active_none():
    assert is_active(None) is False


def test_is_active_no_cpe():
    sub = (1, "active", "pm_123", None, None, 39900, "RUB", "a@b.com", None, None, "month", 0, False)
    assert is_active(sub) is False


def test_is_active_active_future_cpe():
    future = datetime.now(timezone.utc) + timedelta(days=10)
    sub = (1, "active", "pm_123", future, None, 39900, "RUB", "a@b.com", None, None, "month", 0, False)
    assert is_active(sub) is True


def test_is_active_cancelled_with_include():
    future = datetime.now(timezone.utc) + timedelta(days=10)
    sub = (1, "cancelled", "pm_123", future, None, 39900, "RUB", "a@b.com", None, None, "month", 0, False)
    assert is_active(sub, include_cancelled=True) is True
    assert is_active(sub, include_cancelled=False) is False


def test_is_active_expired():
    past = datetime.now(timezone.utc) - timedelta(days=1)
    sub = (1, "active", "pm_123", past, None, 39900, "RUB", "a@b.com", None, None, "month", 0, False)
    assert is_active(sub) is False


def test_is_active_cpe_as_string():
    future = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
    sub = (1, "active", "pm_123", future, None, 39900, "RUB", "a@b.com", None, None, "month", 0, False)
    assert is_active(sub) is True


def test_is_active_naive_cpe():
    # naive datetime treated as UTC
    future = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=10)
    sub = (1, "active", "pm_123", future, None, 39900, "RUB", "a@b.com", None, None, "month", 0, False)
    assert is_active(sub) is True


def test_next_month_basic():
    dt = datetime(2025, 1, 15, tzinfo=timezone.utc)
    assert _next_month(dt) == datetime(2025, 2, 15, tzinfo=timezone.utc)


def test_next_month_december():
    dt = datetime(2025, 12, 15, tzinfo=timezone.utc)
    assert _next_month(dt) == datetime(2026, 1, 15, tzinfo=timezone.utc)


def test_next_month_day_overflow():
    dt = datetime(2025, 1, 31, tzinfo=timezone.utc)
    result = _next_month(dt)
    assert result == datetime(2025, 2, 28, tzinfo=timezone.utc)


def test_add_months():
    dt = datetime(2025, 1, 15, tzinfo=timezone.utc)
    result = _add_months(dt, 12)
    assert result == datetime(2026, 1, 15, tzinfo=timezone.utc)


def test_calc_renewal_dates_from_future_cpe():
    now = datetime(2025, 6, 1, tzinfo=timezone.utc)
    cpe = datetime(2025, 6, 15, tzinfo=timezone.utc)
    new_cpe, nca = _calc_renewal_dates(cpe, now, 1)
    assert new_cpe == datetime(2025, 7, 15, tzinfo=timezone.utc)
    assert nca == new_cpe - timedelta(days=1)


def test_calc_renewal_dates_from_expired_cpe():
    now = datetime(2025, 6, 15, tzinfo=timezone.utc)
    cpe = datetime(2025, 6, 1, tzinfo=timezone.utc)
    new_cpe, _nca = _calc_renewal_dates(cpe, now, 1)
    # should anchor from now since cpe is in the past
    assert new_cpe == _next_month(now)


def test_calc_renewal_dates_string_cpe():
    now = datetime(2025, 6, 1, tzinfo=timezone.utc)
    cpe_str = "2025-06-15T00:00:00+00:00"
    new_cpe, _nca = _calc_renewal_dates(cpe_str, now, 1)
    assert new_cpe == datetime(2025, 7, 15, tzinfo=timezone.utc)


def test_calc_renewal_dates_none_cpe():
    now = datetime(2025, 6, 1, tzinfo=timezone.utc)
    new_cpe, _nca = _calc_renewal_dates(None, now, 1)
    assert new_cpe == _next_month(now)
