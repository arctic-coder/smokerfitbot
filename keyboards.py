from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from texts import (
    BTN_CANCEL_PAYMENT,
    BTN_CHECK_PAYMENT,
    BTN_DONE,
    BTN_FILL_FORM,
    BTN_JUNIOR,
    BTN_MUSCLE_BACK_MORE,
    BTN_MUSCLE_BELLY_MORE,
    BTN_MUSCLE_BREAST_MORE,
    BTN_MUSCLE_CALVES,
    BTN_MUSCLE_LEGS_MORE,
    BTN_MUSCLE_SHOULDERS,
    BTN_MUSCLE_TRICEPC,
    BTN_NO_NEED,
    BTN_RETURN_TO_PAYMENT,
    BTN_USE_EXISTING_FORM,
    DURATION,
    DURATION_BEGINNER,
    EQUIPMENT,
    LEVELS,
    LIMITATIONS,
    start_sub_month_label,
    start_sub_year_label,
)


def _mk(rows, one_time: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=str(x)) for x in row] for row in rows]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=one_time)


# стартовые кнопки
start_kb = _mk([[BTN_FILL_FORM, BTN_USE_EXISTING_FORM]])

# уровень подготовки
level_kb = _mk([[x] for x in LEVELS])

# ограничения + "Готово"
limitations_kb = _mk(
    [
        LIMITATIONS[:3],
        LIMITATIONS[3:],
        [BTN_DONE],
    ]
)

# инвентарь + "Готово"
equipment_kb = _mk(
    [
        EQUIPMENT[0:3],
        EQUIPMENT[3:6],
        EQUIPMENT[6:9],
        [*EQUIPMENT[9:], BTN_DONE],
    ]
)


def kb_choose_plan() -> InlineKeyboardMarkup:
    return kb_choose_plan_with_prices()


def kb_choose_plan_with_prices(
    price_month_cents: int | None = None, price_year_cents: int | None = None
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=start_sub_month_label(price_month_cents), callback_data="go_subscribe:month")],
            [InlineKeyboardButton(text=start_sub_year_label(price_year_cents), callback_data="go_subscribe:year")],
        ]
    )


# длительность
def duration_kb_for(level: str) -> ReplyKeyboardMarkup:
    if level == BTN_JUNIOR:
        return _mk([DURATION_BEGINNER], one_time=True)
    return _mk([DURATION], one_time=True)


def extras_kb() -> ReplyKeyboardMarkup:
    rows = [
        [BTN_MUSCLE_TRICEPC, BTN_MUSCLE_SHOULDERS, BTN_MUSCLE_CALVES],
        [BTN_MUSCLE_BACK_MORE, BTN_MUSCLE_LEGS_MORE, BTN_MUSCLE_BELLY_MORE],
        [BTN_MUSCLE_BREAST_MORE, BTN_NO_NEED, BTN_DONE],
    ]
    return _mk(rows)


def kb_promo_prompt() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Перейти к оплате без промокода", callback_data="promo_skip")],
        ]
    )


def kb_subscribe(url: str | None) -> InlineKeyboardMarkup:
    if url:
        return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=BTN_RETURN_TO_PAYMENT, url=url)]]
        )
    return kb_choose_plan()


def kb_payment_pending(payment_id: str, url: str | None) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if url:
        rows.append([InlineKeyboardButton(text=BTN_RETURN_TO_PAYMENT, url=url)])
    rows.append([InlineKeyboardButton(text=BTN_CHECK_PAYMENT, callback_data=f"chkpay:{payment_id}")])
    rows.append([InlineKeyboardButton(text=BTN_CANCEL_PAYMENT, callback_data=f"cancelpay:{payment_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
