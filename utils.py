import json
import random

def load_exercises():
    with open("exercises.json", encoding="utf-8") as f:
        return json.load(f)

def generate_workout(user_data):
    level = user_data.get("level").lower()
    limitations = user_data.get("limitations", [])
    equipment = user_data.get("equipment", [])

    all_ex = load_exercises()

    # фильтрация
    filtered = []
    for ex in all_ex:
        if level not in [lvl.lower() for lvl in ex["level"]]:
            continue
        if any(lim in ex["limitations"] for lim in limitations):
            continue
        if any(req not in equipment for req in ex["equipment"]):
            continue
        filtered.append(ex)

    # выбрать случайные упражнения по группам мышц
    result = []
    used_groups = set()
    for ex in filtered:
        if ex["group"] not in used_groups:
            result.append(ex)
            used_groups.add(ex["group"])

    return result