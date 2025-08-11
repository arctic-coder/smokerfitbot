import json
import random

def load_exercises():
    with open("exercises.json", encoding="utf-8") as f:
        return json.load(f)

# Временная заглушка: вернём фиксированный набор.
# Позже подключим отбор из таблицы exercises.
def generate_workout(user_data):
    return [
        {"name": "Подтягивания на резинке", "link": "https://example.com/tech/pullup-band"},
        {"name": "Планка с колен", "link": "https://example.com/tech/knee-plank"},
        {"name": "Приседания со штангой на плечах", "link": "https://example.com/tech/back-squat"},
        {"name": "Пистолетики", "link": "https://example.com/tech/pistol-squat"},
    ]
