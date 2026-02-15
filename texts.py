"""
texts.py — все человеко-читаемые строки и подписи на кнопках
"""

import os

SUBSCRIPTION_PRICE_MONTH = int(os.getenv("SUBSCRIPTION_PRICE_MONTH", "39900"))
SUBSCRIPTION_PRICE_YEAR = int(os.getenv("SUBSCRIPTION_PRICE_YEAR", "299000"))


def _fmt_rub(cents: int) -> str:
    return f"{cents / 100:.2f}"


def start_sub_month_label(amount_cents: int | None = None) -> str:
    value = _fmt_rub(amount_cents if amount_cents is not None else SUBSCRIPTION_PRICE_MONTH)
    return f"Оформить подписку на месяц {value} ₽"


def start_sub_year_label(amount_cents: int | None = None) -> str:
    value = _fmt_rub(amount_cents if amount_cents is not None else SUBSCRIPTION_PRICE_YEAR)
    return f"Оформить подписку на год {value} ₽"


AMOUNT_MONTH = _fmt_rub(SUBSCRIPTION_PRICE_MONTH)
AMOUNT_YEAR = _fmt_rub(SUBSCRIPTION_PRICE_YEAR)

BTN_START_SUB_MONTH = f"Оформить подписку на месяц {AMOUNT_MONTH} ₽"
BTN_START_SUB_YEAR = f"Оформить подписку на год {AMOUNT_YEAR} ₽"

# --- КНОПКИ ---
BTN_FILL_FORM = "Заполнить анкету заново"
BTN_USE_EXISTING_FORM = "Использовать старую анкету"

BTN_RETURN_TO_PAYMENT = "Перейти к оплате"
BTN_CHECK_PAYMENT = "Проверить оплату"
BTN_CANCEL_PAYMENT = "Отменить платёж"

BTN_CANCEL_YES = "Да, отменить продление"
BTN_CANCEL_NO = "Оставить как есть"
BTN_DONE = "Готово"
BTN_NO_NEED = "Нет, не надо"

BTN_JUNIOR = "Новичок"
BTN_MIDDLE = "Середнячок"
BTN_SENIOR = "Продолжающий"

LEVELS = [
    BTN_JUNIOR,
    BTN_MIDDLE,
    BTN_SENIOR,
]

BTN_5_10 = "5-10 мин"
BTN_15_20 = "15-20 мин"
BTN_35_45 = "35-45 мин"

DURATION = [BTN_5_10, BTN_15_20, BTN_35_45]
DURATION_BEGINNER = [BTN_5_10, BTN_15_20]

BTN_LIMIT_NO = "Нет ограничений"
BTN_LIMIT_KNEES = "Больные колени"
BTN_LIMIT_POZV = "Межпозвоночные грыжи/протрузии"
BTN_LIMIT_WEIGHT = "Большой вес"

LIMITATIONS = [
    BTN_LIMIT_KNEES,
    BTN_LIMIT_POZV,
    BTN_LIMIT_WEIGHT,
    BTN_LIMIT_NO,
]

BTN_MUSCLE_BACK = "Спина"
BTN_MUSCLE_LEGS = "Ноги"
BTN_MUSCLE_BREAST = "Грудь"
BTN_MUSCLE_BELLY = "Живот"
BTN_MUSCLE_TRICEPC = "Трицепсы"
BTN_MUSCLE_SHOULDERS = "Плечи"
BTN_MUSCLE_CALVES = "Икры"
BTN_MUSCLE_BACK_MORE = "Еще на спину"
BTN_MUSCLE_LEGS_MORE = "Еще на низ"
BTN_MUSCLE_BREAST_MORE = "Еще на грудь"
BTN_MUSCLE_BELLY_MORE = "Еще на живот"

BASE_GROUPS = [BTN_MUSCLE_BACK, BTN_MUSCLE_LEGS, BTN_MUSCLE_BREAST, BTN_MUSCLE_BELLY]

EXTRA_MUSCLE_OPTIONS = [
    BTN_MUSCLE_TRICEPC,
    BTN_MUSCLE_SHOULDERS,
    BTN_MUSCLE_CALVES,
    BTN_MUSCLE_BACK_MORE,
    BTN_MUSCLE_LEGS_MORE,
    BTN_MUSCLE_BELLY_MORE,
    BTN_MUSCLE_BREAST_MORE,
    BTN_NO_NEED,
]

EXTRA_BUTTON_TO_GROUP = {
    BTN_MUSCLE_TRICEPC: BTN_MUSCLE_TRICEPC,
    BTN_MUSCLE_SHOULDERS: BTN_MUSCLE_SHOULDERS,
    BTN_MUSCLE_CALVES: BTN_MUSCLE_CALVES,
    BTN_MUSCLE_BACK_MORE: BTN_MUSCLE_BACK,
    BTN_MUSCLE_LEGS_MORE: BTN_MUSCLE_LEGS,
    BTN_MUSCLE_BELLY_MORE: BTN_MUSCLE_BELLY,
    BTN_MUSCLE_BREAST_MORE: BTN_MUSCLE_BREAST,
    BTN_NO_NEED: None,
}

BTN_EQUIP_THICK_BAND = "Толстая резинка"
BTN_EQUIP_THIN_BAND = "Тонкая резинка"
BTN_EQUIP_LOOPS = "Петли"
BTN_EQUIP_SMALL_DUMPBELLS = "Маленькие гантели"
BTN_EQUIP_COLLAPS_DUMPBELLS = "Разборные гантели"
BTN_EQUIP_BAR = "Штанга"
BTN_EQUIP_KETTLEBELL = "Гиря"
BTN_EQUIP_HORIZONTAL_BAR = "Турник"
BTN_EQUIP_GYM = "Тренажерный зал"
BTN_EQUIP_NONE = "Ничего"

EQUIPMENT = [
    BTN_EQUIP_THICK_BAND,
    BTN_EQUIP_THIN_BAND,
    BTN_EQUIP_LOOPS,
    BTN_EQUIP_SMALL_DUMPBELLS,
    BTN_EQUIP_COLLAPS_DUMPBELLS,
    BTN_EQUIP_BAR,
    BTN_EQUIP_KETTLEBELL,
    BTN_EQUIP_HORIZONTAL_BAR,
    BTN_EQUIP_GYM,
    BTN_EQUIP_NONE,
]

# --- СООБЩЕНИЯ (общие) ---
START_MESSAGE = (
    "Привет, это конструктор силовых тренировок от “Физкультуры курильщика”!\n\n"
    'Держите <a href="https://telegra.ph/Kak-polzovatsya-Smokerfitbot-10-22">памятку</a>. Если вы генерируете тренировку впервые, обязательно прочтите ее, прежде чем начинать, - там написано, что вообще с этой тренировкой делать и как не перестараться.\n\n'
    "<b>Ну и поехали!</b>"
)
INVALID_CHOICE = "Пожалуйста, выбери из предложенных кнопок."
PROFILE_NOT_FOUND = "Анкета не найдена. Пожалуйста, заполните её заново."

# --- АНКЕТА ---
LEVEL_PROMPT = (
    "Какой у вас опыт регулярных занятий силовыми? \n\n"
    "- Новичок (прям совсем)\n"
    "- Середнячок (от нескольких месяцев до года)\n"
    "- Продолжающий (больше года)\n"
)
LIMITATIONS_PROMPT = "Какие у вас есть медицинские ограничения? (Нажмите “Готово”, когда выберете все)"
EQUIPMENT_PROMPT = (
    "Какой инвентарь у вас есть? (Выберите все нужные варианты и нажмите “Готово”).\n"
    'Если непонятно, что имеется в виду, <a href="https://telegra.ph/Inventar-10-15">вот здесь</a> есть пояснения'
)
DURATION_PROMPT = "Сколько времени у вас есть на тренировку?"
EXTRAS_PROMPT = (
    "Вы хотите помимо базовых упражнений на спину, грудь, низ и живот добавить что-то еще?\n"
    "Выберите до двух вариантов и нажмите 'Готово'."
)

WORKOUT_STARTING = "Отлично, генерирую тренировку!..."
WORKOUT_EMPTY = "К сожалению, не удалось подобрать подходящие упражнения 😢"
WORKOUT_HEADER = "Вот она:"
WORKOUT_FOOTER = 'Если что-то непонятно, загляните еще раз в <a href="https://telegra.ph/Kak-polzovatsya-Smokerfitbot-10-22">памятку</a>. А про инвентарь все написано <a href="https://telegra.ph/Inventar-10-15">здесь</a>.'

# --- ПОДПИСКА / ПЛАТЕЖИ ---
SUB_REQUIRED = "Вы уже использовали бесплатную тренировку.\nТеперь можно выбрать подписку с ежегодной или ежемесячной оплатой. Отменить ее можно будет в любой момент командой /cancel"

SUB_ALREADY_ACTIVE = "У вас уже активная подписка{cancelled} ✅\nОплачено до: {cpe}\n\nКоманда: /status"

EMAIL_PROMPT = "Введите e-mail для отправки чека:"
EMAIL_INVALID = "Неверный e-mail. Введите корректный адрес:"

PAYMENT_SUCCEEDED = "Оплата прошла! Подписка активна ✅"
PAYMENT_PENDING = "Платёж ещё не подтверждён. Если вы оплатили — подождите минуту и нажмите /check снова."
PAYMENT_FAILED = "Платёж не прошёл или был отменён. Попробуйте /subscribe ещё раз."
PAYMENT_CHECK_FAILED = "Не получилось проверить платёж, попробуйте /check чуть позже."
NO_PENDING_PAYMENTS = "Спасибо! Чтобы проверить статус подписки, выберите команду /status "
STATUS_NOT_SET = "Статус: подписка не оформлена."
STATUS_LINE = "Статус подписки: {status}"
STATUS_PAID_TILL = "Доступ (оплачено) до: {cpe}"
STATUS_NEXT_CHARGE = "Следующее списание: {nca} (≈ за 1 день до окончания) {amount} ₽"
STATUS_FOOTER = "\nКоманды: /subscribe — оформить, /cancel — отключить продление"

CANCEL_ASK = "Вы уверены, что хотите отменить продление? Доступ сохранится до конца оплаченного периода (до {cpe})."
CANCEL_ALREADY = "Продление уже отключено. Доступ — до {cpe}."
CANCEL_DONE = "Продление отключено. Доступ сохранится до конца оплаченного периода. /status"
CANCEL_NOT_ACTIVE = "Подписка не активна."
CANCEL_NONE = "Подписка не оформлена."
CANCEL_CURRENT = "Текущий платёж отменён"
SUBSCRIBE_CREATE = "Оформление подписки: оплатите по ссылке ниже."
SUBSCRIBE_RESUME_FAIL = "Не удалось создать/возобновить платёж. Попробуйте позже."
SUBSCRIBE_YK_REJECT = "ЮKassa отклонила запрос: {desc}"
SUBSCRIBE_PROMPT = "Оформление подписки."
SUBSCRIBE_FROM_COMMAND = "Выберите подписку — на месяц или на год.\nПодписка продлевается автоматически по выбранному плану. Отменить можно в любой момент командой /cancel"

HELP = "Если что-то сломалось, пишите сюда: @halemaumau"

# --- Промокоды ---
PROMO_PROMPT = "Есть промокод? Введите его сообщением или переходите к оплате без промокода."
PROMO_INVALID = "Промокод не найден или неактивен. Попробуйте снова или продолжите без промокода."
PROMO_APPLIED = "Промокод применён. Выберите план с промо-ценой."

# --- Уведомления автосписаний ---
RECURRING_PRECHARGE = "Напоминание: завтра спишем продление подписки."
RECURRING_SUCCESS = "Подписка продлена успешно ✅"
RECURRING_FAILED_RETRY = "Не удалось продлить подписку ❌. Повторим попытку завтра."
RECURRING_FAILED_RETRY_LAST = "Не удалось продлить подписку ❌. Вы можете оформить подписку заново /subscribe."
