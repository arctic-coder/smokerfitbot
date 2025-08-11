import json
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher
from aiogram.types import ReplyKeyboardRemove

from states import Form
from utils import generate_workout
from db import get_user, save_user
from keyboards import start_kb, level_kb, limitations_kb, equipment_kb, duration_kb
from constants import LEVELS, LIMITATIONS, EQUIPMENT, DURATION_MINUTES

# множества для быстрых проверок
LEVELS_SET = set(LEVELS)                 # строки
LIMITATIONS_SET = set(LIMITATIONS)       # строки (включая "Нет ограничений")
EQUIPMENT_SET = set(EQUIPMENT)           # строки (включая "Ничего")
DURATION_SET = {str(x) for x in DURATION_MINUTES}  # сравниваем со строками из Telegram

def register_handlers(dp: Dispatcher) -> None:

    # --- старт и выбор режима ---
    @dp.message_handler(commands='start')
    async def start_handler(message: types.Message, state: FSMContext):
        await state.finish()
        await message.answer(
            "Привет! Я — Конструктор тренировок от Физкультуры курильщика 🏋️‍♀️\n\n"
            "Выберите действие:",
            reply_markup=start_kb
        )

    @dp.message_handler(lambda m: m.text == "Заполнить анкету заново")
    async def handle_new_form(message: types.Message, state: FSMContext):
        await state.finish()
        await Form.level.set()
        await message.answer("Выберите уровень подготовки:", reply_markup=level_kb)

    @dp.message_handler(lambda m: m.text == "Использовать текущую анкету")
    async def handle_existing_form(message: types.Message, state: FSMContext):
        row = await get_user(message.from_user.id)
        if not row:
            return await message.answer("Анкета не найдена. Пожалуйста, заполните её заново.")

        _, level, limitations_json, equipment_json, _duration_saved = row
        limitations = json.loads(limitations_json) if limitations_json else []
        equipment = json.loads(equipment_json) if equipment_json else []

        # кладём в state и просим выбрать длительность
        await state.update_data(level=level, limitations=limitations, equipment=equipment)
        await Form.duration.set()
        text = (
            "📋 Ваша анкета:\n"
            f"• Уровень: {level}\n"
            f"• Ограничения: {', '.join(limitations) if limitations else 'Нет'}\n"
            f"• Инвентарь: {', '.join(equipment) if equipment else 'Нет'}\n\n"
            "Выберите длительность тренировки:"
        )
        await message.answer(text, reply_markup=duration_kb)

    # --- анкета ---
    @dp.message_handler(state=Form.level)
    async def process_level(message: types.Message, state: FSMContext):
        if message.text not in LEVELS_SET:
            return await message.answer("Пожалуйста, выбери из предложенных кнопок.", reply_markup=level_kb)
        await state.update_data(level=message.text, limitations=[])
        await Form.limitations.set()
        await message.answer("Выберите ограничения (по одному, нажмите 'Готово' когда закончите):", reply_markup=limitations_kb)

    @dp.message_handler(state=Form.limitations)
    async def process_limitations(message: types.Message, state: FSMContext):
        data = await state.get_data()
        current = data.get("limitations", [])

        if message.text == "Готово":
            await state.update_data(limitations=current, equipment=[])
            await Form.equipment.set()
            return await message.answer("Выберите инвентарь (по одному, нажмите 'Готово' когда закончите):", reply_markup=equipment_kb)

        if message.text not in LIMITATIONS_SET:
            return await message.answer("Пожалуйста, выбери из кнопок.", reply_markup=limitations_kb)

        # если выбрано "Нет ограничений" — очищаем остальные и фиксируем только его
        if message.text == "Нет ограничений":
            await state.update_data(limitations=["Нет ограничений"])
            return

        # иначе добавляем, убрав "Нет ограничений", если оно там было
        if "Нет ограничений" in current:
            current = []

        if message.text not in current:
            current.append(message.text)
            await state.update_data(limitations=current)

    @dp.message_handler(state=Form.equipment)
    async def process_equipment(message: types.Message, state: FSMContext):
        data = await state.get_data()
        current = data.get("equipment", [])

        if message.text == "Готово":
            await state.update_data(equipment=current)
            await Form.duration.set()
            return await message.answer("Выберите длительность тренировки:", reply_markup=duration_kb)

        if message.text not in EQUIPMENT_SET:
            return await message.answer("Пожалуйста, выбери из кнопок.", reply_markup=equipment_kb)

        # если выбран вариант "Ничего" — сбрасываем остальные
        if message.text == "Ничего":
            await state.update_data(equipment=["Ничего"])
            return

        # если ранее было "Ничего" — убираем его
        if "Ничего" in current:
            current = []

        if message.text not in current:
            current.append(message.text)
            await state.update_data(equipment=current)

    @dp.message_handler(state=Form.duration)
    async def process_duration(message: types.Message, state: FSMContext):
        if message.text not in DURATION_SET:
            return await message.answer("Пожалуйста, выбери из кнопок.", reply_markup=duration_kb)

        duration = int(message.text)
        await state.update_data(duration_minutes=duration)

        user_data = await state.get_data()
        await message.answer("Спасибо! Генерирую тренировку...", reply_markup=ReplyKeyboardRemove())

        workout = generate_workout(user_data)  # сейчас заглушка
        if not workout:
            await message.answer("К сожалению, не удалось подобрать подходящие упражнения 😢")
        else:
            text = "Ваша тренировка:\n\n"
            for i, ex in enumerate(workout, start=1):
                text += f"{i}. {ex['name']}\nСсылка: {ex['link']}\n\n"
            await message.answer(text)

        await save_user(
            user_id=message.from_user.id,
            level=user_data['level'],
            limitations=user_data['limitations'],
            equipment=user_data['equipment'],
            duration_minutes=user_data['duration_minutes']
        )
        await state.finish()
