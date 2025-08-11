from aiogram.types import ReplyKeyboardMarkup

start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add("Заполнить анкету заново", "Использовать текущую анкету")

level_kb = ReplyKeyboardMarkup(resize_keyboard=True)
level_kb.add("Новичок", "1–2 года", "3+ лет")

limitations_kb = ReplyKeyboardMarkup(resize_keyboard=True)
limitations_kb.add("Грыжи", "Больные колени", "Ожирение")
limitations_kb.add("Нет ограничений", "Готово")

equipment_kb = ReplyKeyboardMarkup(resize_keyboard=True)
equipment_kb.add("Гантели", "Штанга", "Турник", "Резинки")
equipment_kb.add("Нет", "Готово")

duration_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
duration_kb.add("15", "30", "45")

#todo constants