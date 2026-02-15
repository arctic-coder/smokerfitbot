# tests/test_utils.py
from unittest.mock import AsyncMock, patch

from utils import _equipment_options_ok, _level_ok, _limitations_ok, _pick_one, _to_items, generate_workout


def test_level_ok_empty_levels():
    assert _level_ok("Новичок", []) is True


def test_level_ok_match():
    assert _level_ok("Новичок", ["Новичок", "Середнячок"]) is True


def test_level_ok_no_match():
    assert _level_ok("Продолжающий", ["Новичок"]) is False


def test_limitations_ok_no_limits():
    assert _limitations_ok([], ["Больные колени"]) is True


def test_limitations_ok_no_restrictions():
    assert _limitations_ok(["Нет ограничений"], ["Больные колени"]) is True


def test_limitations_ok_allowed():
    assert _limitations_ok(["Больные колени"], ["Больные колени", "Большой вес"]) is True


def test_limitations_ok_not_allowed():
    assert _limitations_ok(["Больные колени", "Большой вес"], ["Больные колени"]) is False


def test_limitations_ok_empty_ex_allowed():
    assert _limitations_ok(["Больные колени"], []) is True


def test_equipment_ok_no_options():
    assert _equipment_options_ok(["Гиря"], []) is True


def test_equipment_ok_nothing():
    assert _equipment_options_ok([], [["Ничего"]]) is True


def test_equipment_ok_subset():
    assert _equipment_options_ok(["Гиря", "Штанга"], [["Гиря"]]) is True


def test_equipment_ok_not_subset():
    assert _equipment_options_ok(["Гиря"], [["Штанга"]]) is False


def test_equipment_ok_multiple_options():
    assert _equipment_options_ok(["Гиря"], [["Штанга"], ["Гиря"]]) is True


def test_pick_one_avoids_used():
    pool = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
    result = _pick_one(pool, {"A", "B"})
    assert result is not None
    assert result["name"] == "C"


def test_pick_one_empty_pool():
    assert _pick_one([], set()) is None


def test_pick_one_all_used_allows_repeat():
    pool = [{"name": "A"}]
    result = _pick_one(pool, {"A"})
    assert result is not None
    assert result["name"] == "A"


def test_to_items_basic():
    exercises = [
        {"name": "Push-up", "muscle_group": "Грудь", "reps_note": "15", "video_url": "http://example.com"},
        None,
        {"name": "Squat", "muscle_group": "Ноги", "reps_note": "", "video_url": ""},
    ]
    items = _to_items(exercises, sets=3)
    assert len(items) == 2
    assert items[0]["name"] == "Push-up"
    assert items[0]["sets"] == 3
    assert items[0]["reps"] == "15"
    assert items[0]["link"] == "http://example.com"
    assert items[1]["reps"] == "10"  # default


async def test_generate_workout_5_10():
    exercises = [
        {"name": f"Ex_{g}_{i}", "levels": ["Новичок"], "equipment": [], "equipment_dnf": [["Ничего"]],
         "allowed_limitations": [], "muscle_group": g, "reps_note": "10", "video_url": ""}
        for g in ["Спина", "Ноги", "Грудь", "Живот"]
        for i in range(3)
    ]
    with patch("utils.get_all_exercises", new=AsyncMock(return_value=exercises)):
        plan = await generate_workout({
            "level": "Новичок",
            "limitations": [],
            "equipment": [],
            "duration_minutes": "5-10 мин",
        })
    assert len(plan) == 4
    for item in plan:
        assert item["sets"] == 1


async def test_generate_workout_empty_on_bad_duration():
    with patch("utils.get_all_exercises", new=AsyncMock(return_value=[])):
        plan = await generate_workout({
            "level": "Новичок",
            "limitations": [],
            "equipment": [],
            "duration_minutes": "unknown",
        })
    assert plan == []


async def test_generate_workout_35_45_with_extras():
    exercises = [
        {"name": f"Ex_{g}_{i}", "levels": [], "equipment": [], "equipment_dnf": [],
         "allowed_limitations": [], "muscle_group": g, "reps_note": "10", "video_url": ""}
        for g in ["Спина", "Ноги", "Грудь", "Живот", "Трицепсы", "Плечи"]
        for i in range(3)
    ]
    with patch("utils.get_all_exercises", new=AsyncMock(return_value=exercises)):
        plan = await generate_workout({
            "level": "Середнячок",
            "limitations": [],
            "equipment": [],
            "duration_minutes": "35-45 мин",
            "extras": ["Трицепсы", "Плечи"],
        })
    # 4 base groups (3 sets each) + 2 extras (2 sets each)
    assert len(plan) == 6
    base_items = [p for p in plan if p["sets"] == 3]
    extra_items = [p for p in plan if p["sets"] == 2]
    assert len(base_items) == 4
    assert len(extra_items) == 2
