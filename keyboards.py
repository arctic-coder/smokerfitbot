from aiogram.types import ReplyKeyboardMarkup
from constants import LEVELS, EQUIPMENT, LIMITATIONS, DURATION

def _mk(rows, one_time: bool = False) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time)
    for r in rows:
        #приводим каждую кнопку к строке
        kb.row(*[str(x) for x in r])
    return kb

# стартовые кнопки
start_kb = _mk([["Заполнить анкету заново", "Использовать текущую анкету"]])

# уровень подготовки
level_kb = _mk([LEVELS])

# ограничения + "Готово"
limitations_kb = _mk([
    LIMITATIONS[:3],
    LIMITATIONS[3:],
    ["Готово"],
])

# инвентарь + "Готово"
equipment_kb = _mk([
    EQUIPMENT[0:3],
    EQUIPMENT[3:6],
    EQUIPMENT[6:9],
    EQUIPMENT[9:] + ["Готово"],
])

# длительность
duration_kb = _mk([DURATION], one_time=True)
