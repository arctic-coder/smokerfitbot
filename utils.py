# utils.py
import random
from typing import Iterable
from db import get_all_exercises
from texts import BASE_GROUPS, BTN_15_20, BTN_35_45, BTN_5_10, BTN_EQUIP_NONE, BTN_LIMIT_NO, EXTRA_BUTTON_TO_GROUP

# ---- фильтры совместимости ----

def _level_ok(user_level: str, ex_levels: list[str]) -> bool:
    # если у упражнения уровни не заданы — подходит всем
    return not ex_levels or (user_level in ex_levels)

def _limitations_ok(user_limits: list[str], ex_allowed: list[str]) -> bool:
    # «Нет ограничений» или пусто — всё ок
    if not user_limits or BTN_LIMIT_NO in user_limits:
        return True
    # если упражнение не ограничивает — трактуем как «можно всем»
    if not ex_allowed:
        return True
    # все ограничения пользователя должны быть разрешены упражнением
    return all(l in ex_allowed for l in user_limits)

# utils.py

def _equipment_options_ok(user_eq: list[str], options: list) -> bool:
    """
    options — list[list[str]] (варианты наборов инвентаря).
    True, если есть опция, целиком покрываемая пользовательским набором.
    Спец-случай: ["Ничего"] — подходит ВСЕГДА (упражнение без инвентаря).
    """
    user_set = set(user_eq or [])
    if not options:
        return True
    for opt in options:
        if not isinstance(opt, list):
            continue
        opt_norm = [str(x).strip() for x in opt if str(x).strip()]
        # КЛЮЧЕВАЯ ПРАВКА: разрешаем безинвентарные упражнения при любом наборе пользователя
        if opt_norm == [BTN_EQUIP_NONE]:
            return True
        # обычный случай: весь требуемый инвентарь есть у пользователя
        if set(opt_norm).issubset(user_set):
            return True
    return False


# ---- сборка плана ----

def _pick_one(pool: list[dict], used_names: set[str]) -> dict | None:
    """Берём случайное упражнение из группы, желательно без повторов по имени."""
    candidates = [ex for ex in pool if ex["name"] not in used_names]
    if not candidates:
        candidates = pool[:]  # если всё уже использовали — допускаем повтор
    return random.choice(candidates) if candidates else None

def _to_items(ex_list: Iterable[dict], sets: int) -> list[dict]:
    items = []
    for ex in ex_list:
        if not ex:
            continue
        items.append({
            "name":  ex["name"],
            "group": ex.get("muscle_group") or "",
            "sets":  sets,
            # по ТЗ «сколько там повторений в таблице» — показываем reps_note как есть
            "reps":  ex.get("reps_note") or "10",
            "link":  ex.get("video_url") or "",
        })
    return items

async def generate_workout(user_data: dict) -> list[dict]:
    """
    Формирует тренировку по ТЗ.
    Вход: level:str, limitations:list[str], equipment:list[str], duration_minutes:str, (опц.) extras:list[str]
    Выход: список шагов: {name, group, sets, reps, link}
    """
    level   = user_data.get("level", "")
    limits  = user_data.get("limitations", []) or []
    equip   = user_data.get("equipment", []) or []
    dur     = user_data.get("duration_minutes", "")

    # 1) Загружаем упражнения из БД и фильтруем
    all_ex = await get_all_exercises()
    filtered = [
        ex for ex in all_ex
        if _level_ok(level, ex.get("levels", []))
        and _limitations_ok(limits, ex.get("allowed_limitations", []))
        and _equipment_options_ok(equip, ex.get("equipment_dnf", []))
    ]

    # 2) Разбиваем по группам
    by_group: dict[str, list[dict]] = {}
    for ex in filtered:
        g = ex.get("muscle_group") or ""
        by_group.setdefault(g, []).append(ex)

    used_names: set[str] = set()
    plan: list[dict] = []

    # 3) Логика по длительности
    if dur == BTN_5_10:
        # базовые группы по 1 упражнению, сетов = 1
        picks = [_pick_one(by_group.get(g, []), used_names) for g in BASE_GROUPS]
        used_names.update(ex["name"] for ex in picks if ex)
        plan = _to_items(picks, sets=1)

    elif dur == BTN_15_20:
        # базовые группы по 1 упражнению, сетов = 2
        picks = [_pick_one(by_group.get(g, []), used_names) for g in BASE_GROUPS]
        used_names.update(ex["name"] for ex in picks if ex)
        plan = _to_items(picks, sets=2)

    elif dur == BTN_35_45:
        # нормализуем «доп. группы»
        raw_extras = user_data.get("extras", []) or []
        extras_groups = []
        for btn in raw_extras:
            grp = EXTRA_BUTTON_TO_GROUP.get(btn)
            if grp and grp not in extras_groups:
                extras_groups.append(grp)
        extras_groups = extras_groups[:2]

        if not extras_groups:
            # без добавок: базовые по 4 подхода
            picks = [_pick_one(by_group.get(g, []), used_names) for g in BASE_GROUPS]
            used_names.update(ex["name"] for ex in picks if ex)
            plan = _to_items(picks, sets=4)
        else:
            # с добавками: базовые по 3, добавки по 2
            base_picks = [_pick_one(by_group.get(g, []), used_names) for g in BASE_GROUPS]
            used_names.update(ex["name"] for ex in base_picks if ex)
            plan = _to_items(base_picks, sets=3)

            add_picks = []
            for g in extras_groups:
                ex = _pick_one(by_group.get(g, []), used_names)
                if ex:
                    used_names.add(ex["name"])
                    add_picks.append(ex)
            plan.extend(_to_items(add_picks, sets=2))
    else:
        plan = []

    return plan
