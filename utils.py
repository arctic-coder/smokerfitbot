# utils.py
import random
from typing import Iterable
from db import get_all_exercises
from texts import BASE_GROUPS, BTN_15_20, BTN_35_45, BTN_5_10, BTN_EQUIP_NONE, BTN_LIMIT_NO, EXTRA_BUTTON_TO_GROUP
import logging
log = logging.getLogger("workout")

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
        if opt_norm == [BTN_EQUIP_NONE]:
            return True
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
            "reps":  ex.get("reps_note") or "10",
            "link":  ex.get("video_url") or "",
        })
    return items

# замени на это
async def generate_workout(user_data: dict) -> list[dict]:
    """
    Формирует тренировку по ТЗ.
    Вход: level:str, limitations:list[str], equipment:list[str], duration_minutes:str, (опц.) extras:list[str]
    Выход: список шагов: {name, group, sets, reps, link}
    """
    level  = str(user_data.get("level", "") or "")
    limits = list(user_data.get("limitations") or [])
    equip  = list(user_data.get("equipment") or [])
    dur    = str(user_data.get("duration_minutes", "") or "")
    extras_raw = list(user_data.get("extras") or [])

    # входные данные
    log.debug("generate_workout: input level=%r limits=%r equip=%r dur=%r extras=%r",
              level, limits, equip, dur, extras_raw)

    # 1) Загружаем упражнения
    all_ex = await get_all_exercises()
    log.debug("generate_workout: total_exercises=%d", len(all_ex))

    # 1a) Поэтапные фильтры — чтобы понять, где «съедается» пул
    after_lvl = [ex for ex in all_ex if _level_ok(level, ex.get("levels", []))]
    log.debug("filter: after level -> %d", len(after_lvl))

    after_lim = [ex for ex in after_lvl if _limitations_ok(limits, ex.get("allowed_limitations", []))]
    log.debug("filter: after limitations -> %d", len(after_lim))

    filtered = [ex for ex in after_lim if _equipment_options_ok(equip, ex.get("equipment_dnf", []))]
    log.debug("filter: after equipment -> %d", len(filtered))

    # 2) Разбиваем по группам
    by_group: dict[str, list[dict]] = {}
    for ex in filtered:
        g = (ex.get("muscle_group") or "").strip()
        by_group.setdefault(g, []).append(ex)

    # диагностируем пустые базовые группы
    missing = [g for g in BASE_GROUPS if not by_group.get(g)]
    if missing:
        log.warning("generate_workout: no exercises for base groups=%r", missing)

    # для наглядности — размеры пулов по группам
    sizes_repr = {g: len(by_group.get(g, [])) for g in BASE_GROUPS}
    log.debug("generate_workout: pool sizes per base group=%r", sizes_repr)

    used_names: set[str] = set()
    plan: list[dict] = []

    # 3) Логика по длительности
    if dur == BTN_5_10:
        picks = [_pick_one(by_group.get(g, []), used_names) for g in BASE_GROUPS]
        used_names.update(ex["name"] for ex in picks if ex)
        log.debug("picks 5-10: %r", [ex["name"] for ex in picks if ex])
        plan = _to_items(picks, sets=1)

    elif dur == BTN_15_20:
        picks = [_pick_one(by_group.get(g, []), used_names) for g in BASE_GROUPS]
        used_names.update(ex["name"] for ex in picks if ex)
        log.debug("picks 15-20: %r", [ex["name"] for ex in picks if ex])
        plan = _to_items(picks, sets=2)

    elif dur == BTN_35_45:
        # нормализуем «доп. группы»
        extras_groups: list[str] = []
        for btn in extras_raw:
            grp = EXTRA_BUTTON_TO_GROUP.get(btn)
            if grp and grp not in extras_groups:
                extras_groups.append(grp)
        extras_groups = extras_groups[:2]
        log.debug("extras normalized -> %r", extras_groups)

        if not extras_groups:
            picks = [_pick_one(by_group.get(g, []), used_names) for g in BASE_GROUPS]
            used_names.update(ex["name"] for ex in picks if ex)
            log.debug("picks 35-45 (no extras): %r", [ex["name"] for ex in picks if ex])
            plan = _to_items(picks, sets=4)
        else:
            base_picks = [_pick_one(by_group.get(g, []), used_names) for g in BASE_GROUPS]
            used_names.update(ex["name"] for ex in base_picks if ex)
            log.debug("base picks 35-45 (with extras): %r", [ex["name"] for ex in base_picks if ex])
            plan = _to_items(base_picks, sets=3)

            add_picks = []
            for g in extras_groups:
                ex = _pick_one(by_group.get(g, []), used_names)
                if ex:
                    used_names.add(ex["name"])
                    add_picks.append(ex)
            log.debug("extra picks 35-45: %r", [ex["name"] for ex in add_picks if ex])
            plan.extend(_to_items(add_picks, sets=2))
    else:
        log.warning("generate_workout: unsupported duration value=%r -> empty plan", dur)
        plan = []

    log.debug("generate_workout: final plan size=%d", len(plan))
    return plan
