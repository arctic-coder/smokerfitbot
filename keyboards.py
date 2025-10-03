from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from texts import ( BTN_DONE, BTN_FILL_FORM, BTN_JUNIOR, BTN_MUSCLE_BACK_MORE, 
BTN_MUSCLE_BELLY_MORE, BTN_MUSCLE_BREAST_MORE, BTN_MUSCLE_CALVES, BTN_MUSCLE_LEGS_MORE, 
BTN_MUSCLE_SHOULDERS, BTN_MUSCLE_TRICEPC, BTN_NO_NEED, BTN_USE_EXISTING_FORM, LEVELS, 
EQUIPMENT, LIMITATIONS, DURATION, DURATION_BEGINNER, BTN_RETURN_TO_PAYMENT, 
BTN_CHECK_PAYMENT, BTN_CANCEL_PAYMENT, BTN_START_SUB_MONTH, BTN_START_SUB_YEAR)

def _mk(rows, one_time: bool = False) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time)
    for r in rows:
        #приводим каждую кнопку к строке
        kb.row(*[str(x) for x in r])
    return kb

# стартовые кнопки
start_kb = _mk([[BTN_FILL_FORM, BTN_USE_EXISTING_FORM]])

# уровень подготовки
level_kb = _mk([[x] for x in LEVELS])

# ограничения + "Готово"
limitations_kb = _mk([
    LIMITATIONS[:3],
    LIMITATIONS[3:],
    [BTN_DONE],
])

# инвентарь + "Готово"
equipment_kb = _mk([
    EQUIPMENT[0:3],
    EQUIPMENT[3:6],
    EQUIPMENT[6:9],
    EQUIPMENT[9:] + [BTN_DONE],
])

def kb_choose_plan() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(BTN_START_SUB_MONTH, callback_data="go_subscribe:month"))
    kb.add(InlineKeyboardButton(BTN_START_SUB_YEAR,  callback_data="go_subscribe:year"))
    return kb

# длительность
def duration_kb_for(level: str) -> ReplyKeyboardMarkup:
    if level == BTN_JUNIOR:
        # две кнопки «5-10» и «15-20»
        return _mk([DURATION_BEGINNER], one_time=True)
    # иначе показываем все варианты
    return _mk([DURATION], one_time=True)

def extras_kb() -> ReplyKeyboardMarkup:
    rows = [
        [BTN_MUSCLE_TRICEPC, BTN_MUSCLE_SHOULDERS, BTN_MUSCLE_CALVES],
        [BTN_MUSCLE_BACK_MORE, BTN_MUSCLE_LEGS_MORE, BTN_MUSCLE_BELLY_MORE],
        [BTN_MUSCLE_BREAST_MORE, BTN_NO_NEED, BTN_DONE],
    ]
    return _mk(rows)

def kb_subscribe(url: str | None) -> InlineKeyboardMarkup:
    if url:
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(BTN_RETURN_TO_PAYMENT, url=url))
        return kb
    return kb_choose_plan()

def kb_payment_pending(payment_id: str, url: str | None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    if url:
        kb.add(InlineKeyboardButton(BTN_RETURN_TO_PAYMENT, url=url))
    kb.add(InlineKeyboardButton(BTN_CHECK_PAYMENT,  callback_data=f"chkpay:{payment_id}"))
    kb.add(InlineKeyboardButton(BTN_CANCEL_PAYMENT, callback_data=f"cancelpay:{payment_id}"))
    return kb
