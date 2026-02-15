# tests/test_keyboards.py
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from keyboards import (
    duration_kb_for,
    equipment_kb,
    extras_kb,
    kb_choose_plan,
    kb_choose_plan_with_prices,
    kb_payment_pending,
    kb_promo_prompt,
    kb_subscribe,
    level_kb,
    limitations_kb,
    start_kb,
)


def test_start_kb_type():
    assert isinstance(start_kb, ReplyKeyboardMarkup)


def test_level_kb_type():
    assert isinstance(level_kb, ReplyKeyboardMarkup)


def test_limitations_kb_type():
    assert isinstance(limitations_kb, ReplyKeyboardMarkup)


def test_equipment_kb_type():
    assert isinstance(equipment_kb, ReplyKeyboardMarkup)


def test_duration_kb_junior():
    kb = duration_kb_for("Новичок")
    assert isinstance(kb, ReplyKeyboardMarkup)
    # junior gets fewer options
    texts = [btn.text for row in kb.keyboard for btn in row]
    assert "35-45 мин" not in texts


def test_duration_kb_regular():
    kb = duration_kb_for("Середнячок")
    texts = [btn.text for row in kb.keyboard for btn in row]
    assert "35-45 мин" in texts


def test_extras_kb_type():
    kb = extras_kb()
    assert isinstance(kb, ReplyKeyboardMarkup)


def test_kb_choose_plan_type():
    kb = kb_choose_plan()
    assert isinstance(kb, InlineKeyboardMarkup)
    assert len(kb.inline_keyboard) == 2  # month + year


def test_kb_choose_plan_with_prices():
    kb = kb_choose_plan_with_prices(19900, 149900)
    assert isinstance(kb, InlineKeyboardMarkup)
    texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert any("199.00" in t for t in texts)
    assert any("1499.00" in t for t in texts)


def test_kb_promo_prompt_type():
    kb = kb_promo_prompt()
    assert isinstance(kb, InlineKeyboardMarkup)


def test_kb_subscribe_with_url():
    kb = kb_subscribe("https://example.com/pay")
    assert isinstance(kb, InlineKeyboardMarkup)
    assert kb.inline_keyboard[0][0].url == "https://example.com/pay"


def test_kb_subscribe_without_url():
    kb = kb_subscribe(None)
    assert isinstance(kb, InlineKeyboardMarkup)
    # should fall back to choose plan
    assert len(kb.inline_keyboard) == 2


def test_kb_payment_pending_with_url():
    kb = kb_payment_pending("pay_123", "https://example.com/pay")
    assert isinstance(kb, InlineKeyboardMarkup)
    assert len(kb.inline_keyboard) == 3  # return + check + cancel


def test_kb_payment_pending_without_url():
    kb = kb_payment_pending("pay_123", None)
    assert isinstance(kb, InlineKeyboardMarkup)
    assert len(kb.inline_keyboard) == 2  # check + cancel (no return button)
