# handlers/form.py
import json
import ast
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from states import Form
from utils import generate_workout
from db import get_user, save_user, get_subscription, set_free_workout_used
from keyboards import level_kb, limitations_kb, equipment_kb, duration_kb_for, extras_kb, kb_subscribe, kb_choose_plan
from texts import (
    BTN_35_45, BTN_EQUIP_NONE, BTN_JUNIOR, BTN_LIMIT_NO, BTN_NO_NEED, LEVEL_PROMPT, LIMITATIONS_PROMPT, EQUIPMENT_PROMPT, DURATION_PROMPT, EXTRAS_PROMPT,
    INVALID_CHOICE, PROFILE_NOT_FOUND, WORKOUT_STARTING, WORKOUT_EMPTY, WORKOUT_HEADER,
    BTN_FILL_FORM, BTN_USE_EXISTING_FORM, BTN_DONE, SUB_REQUIRED,
    LEVELS, LIMITATIONS, EQUIPMENT, DURATION, DURATION_BEGINNER, EXTRA_MUSCLE_OPTIONS
)
from billing.service import is_active

LEVELS_SET = set(LEVELS)
LIMITATIONS_SET = set(LIMITATIONS)
EQUIPMENT_SET = set(EQUIPMENT)

def _to_list(v):
    """Нормализует значение в список (JSON-строка, python-repr, одиночная строка…)."""
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, tuple):
        return list(v)
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return []
        # JSON
        try:
            j = json.loads(s)
            if isinstance(j, list):
                return j
            if isinstance(j, str):
                return [j]
        except Exception:
            pass
        # python repr
        try:
            lit = ast.literal_eval(s)
            if isinstance(lit, (list, tuple)):
                return list(lit)
        except Exception:
            pass
        return [s]
    return [str(v)]

async def fill_form_new(message: types.Message, state: FSMContext) -> None:
    await state.finish()
    await Form.level.set()
    await message.answer(LEVEL_PROMPT, reply_markup=level_kb)

async def fill_form_existing(message: types.Message, state: FSMContext) -> None:
    row = await get_user(message.from_user.id)
    if not row:
        await message.answer(PROFILE_NOT_FOUND)
        return

    level = row[1]
    limitations = _to_list(row[2])
    equipment = _to_list(row[3])

    await state.update_data(level=level, limitations=limitations, equipment=equipment)
    await Form.duration.set()

    text = (
        "📋 Ваша анкета:\n"
        f"• Уровень: {level}\n"
        f"• Ограничения: {', '.join(limitations) if limitations else 'Нет'}\n"
        f"• Инвентарь: {', '.join(equipment) if equipment else 'Нет'}\n\n"
        f"{DURATION_PROMPT}"
    )
    await message.answer(text, reply_markup=duration_kb_for(level))

async def level_step(message: types.Message, state: FSMContext) -> None:
    if message.text not in LEVELS_SET:
        await message.answer(INVALID_CHOICE, reply_markup=level_kb)
        return
    await state.update_data(level=message.text, limitations=[])
    await Form.limitations.set()
    await message.answer(LIMITATIONS_PROMPT, reply_markup=limitations_kb)

async def limitations_step(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    current = data.get("limitations", [])

    if message.text == BTN_DONE:
        await state.update_data(limitations=current, equipment=[])
        await Form.equipment.set()
        await message.answer(EQUIPMENT_PROMPT, reply_markup=equipment_kb)
        return

    if message.text not in LIMITATIONS_SET:
        await message.answer(INVALID_CHOICE, reply_markup=limitations_kb)
        return

    if message.text == BTN_LIMIT_NO:
        await state.update_data(limitations=[BTN_LIMIT_NO])
        return

    if BTN_LIMIT_NO in current:
        current = []

    if message.text not in current:
        current.append(message.text)
        await state.update_data(limitations=current)

async def equipment_step(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    current = data.get("equipment", [])

    if message.text == BTN_DONE:
        await state.update_data(equipment=current)
        await Form.duration.set()
        level = (await state.get_data()).get("level")
        await message.answer(DURATION_PROMPT, reply_markup=duration_kb_for(level))
        return

    if message.text not in EQUIPMENT_SET:
        await message.answer(INVALID_CHOICE, reply_markup=equipment_kb)
        return

    if message.text == BTN_EQUIP_NONE:
        await state.update_data(equipment=[BTN_EQUIP_NONE])
        return

    if BTN_EQUIP_NONE in current:
        current = []

    if message.text not in current:
        current.append(message.text)
        await state.update_data(equipment=current)

async def duration_step(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    level = data.get("level")

    allowed = set(DURATION if level != BTN_JUNIOR else DURATION_BEGINNER)
    if message.text not in allowed:
        await message.answer(INVALID_CHOICE, reply_markup=duration_kb_for(level))
        return

    await state.update_data(duration_minutes=message.text)

    user_id = message.from_user.id
    sub = await get_subscription(user_id)
    user_row = await get_user(user_id)
    free_used = bool(user_row[5]) if user_row and len(user_row) >= 6 else False

    if not is_active(sub):
        if not free_used:
            await set_free_workout_used(user_id, True)
        else:
            await message.answer(SUB_REQUIRED, reply_markup=kb_choose_plan())
            return

    if message.text == BTN_35_45:
        await state.update_data(extras=[])
        await Form.extras.set()
        await message.answer(EXTRAS_PROMPT, reply_markup=extras_kb())
        return

    await _generate_and_send_workout(message, state)

async def extras_step(message: types.Message, state: FSMContext) -> None:
    choice = (message.text or "").strip()
    data = await state.get_data()
    current = data.get("extras", []) or []

    if choice == BTN_DONE:
        if len(current) > 2:
            await message.answer("Можно выбрать не более двух пунктов. Сними лишние и нажми «Готово».", reply_markup=extras_kb())
            return
        await state.update_data(extras=current)
        await _generate_and_send_workout(message, state)
        return

    # валидируем по списку опций
    if choice not in (EXTRA_MUSCLE_OPTIONS + [BTN_DONE, BTN_NO_NEED]):
        await message.answer(INVALID_CHOICE, reply_markup=extras_kb())
        return

    if choice == BTN_NO_NEED:
        await state.update_data(extras=[])
        await _generate_and_send_workout(message, state)
        return

    if choice in current:
        await message.answer(f"Уже добавлено: {', '.join(current)}. Нажмите «Готово», когда закончите.", reply_markup=extras_kb())
        return

    if len(current) >= 2:
        await message.answer("Можно выбрать не более двух пунктов. Нажмите «Готово».", reply_markup=extras_kb())
        return

    current.append(choice)
    await state.update_data(extras=current)
    await message.answer(f"Добавлено: {choice}\nВыбрано: {', '.join(current)}\nМожно выбрать ещё {2 - len(current)}.", reply_markup=extras_kb())

async def _generate_and_send_workout(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_data = await state.get_data()

    await message.answer(WORKOUT_STARTING, reply_markup=ReplyKeyboardRemove())
    workout = await generate_workout(user_data)
    if not workout:
        await message.answer(WORKOUT_EMPTY)
    else:
        lines = [WORKOUT_HEADER]
        for i, ex in enumerate(workout, start=1):
            name = ex.get("name") or ex.get("title") or "Упражнение"
            group = f"{ex.get('group')}" if ex.get("group") else ""
            sets_reps = f"{ex.get('sets')} × {ex.get('reps')}" if ex.get("sets") and ex.get("reps") else ""
            url = ex.get("link")
            if url:
                name = f'<a href="{url}">{name}</a>'
            lines.append(f"<b>{group}</b>: {name}: {sets_reps}")
        await message.answer("\n\n".join(lines), parse_mode="HTML")

    # сохраняем анкету
    try:
        limitations = _to_list(user_data.get('limitations'))
        equipment   = _to_list(user_data.get('equipment'))

        await save_user(
            user_id=user_id,
            level=user_data.get('level'),
            limitations=limitations,         
            equipment=equipment,            
            duration_minutes=user_data.get('duration_minutes'),
            extra_groups=user_data.get('extras')
        )
    finally:
        await state.finish()

def register_form_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(fill_form_new, lambda m: m.text == BTN_FILL_FORM, state="*")
    dp.register_message_handler(fill_form_existing, lambda m: m.text == BTN_USE_EXISTING_FORM, state="*")
    dp.register_message_handler(level_step, state=Form.level)
    dp.register_message_handler(limitations_step, state=Form.limitations)
    dp.register_message_handler(equipment_step, state=Form.equipment)
    dp.register_message_handler(duration_step, state=Form.duration)
    dp.register_message_handler(extras_step, state=Form.extras)
