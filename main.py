from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv
import os
import asyncio
import json

from fsm import Form
from utils import generate_workout
from db import init_db, save_user, get_user

# Bot init
load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Keyboards
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

# Handlers
@dp.message_handler(commands='start')
async def start_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Привет! Я — Конструктор тренировок от Физкультуры курильщика 🏋️‍♀️\n\n"
        "Вы можете использовать сохранённую анкету или заполнить новую:",
        reply_markup=start_kb
    )

# @dp.message_handler(commands='go')
# async def go_handler(message: types.Message, state: FSMContext):
#     await state.finish()
#     await Form.level.set()
#     await message.answer("Выберите уровень подготовки:", reply_markup=level_kb)

@dp.message_handler(lambda message: message.text == "Заполнить анкету заново")
async def handle_new_form(message: types.Message, state: FSMContext):
    await state.finish()
    await Form.level.set()
    await message.answer("Выберите уровень подготовки:", reply_markup=level_kb)

@dp.message_handler(lambda message: message.text == "Использовать текущую анкету")
async def handle_existing_form(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user:
        return await message.answer("Анкета не найдена. Пожалуйста, заполните её заново.")

    level = user[1]
    limitations = json.loads(user[2])
    equipment = json.loads(user[3])
    duration_saved = user[4]

    # Сохраняем в state
    await state.update_data(level=level, limitations=limitations, equipment=equipment)
    await Form.duration.set()

    # Показываем анкету
    text = (
        "📋 Ваша анкета:\n"
        f"• Уровень: {level}\n"
        f"• Ограничения: {', '.join(limitations) if limitations else 'Нет'}\n"
        f"• Инвентарь: {', '.join(equipment) if equipment else 'Нет'}\n\n"
        "Выберите длительность тренировки:"
    )
    await message.answer(text, reply_markup=duration_kb)


@dp.message_handler(state=Form.level)
async def process_level(message: types.Message, state: FSMContext):
    if message.text not in ["Новичок", "1–2 года", "3+ лет"]:
        return await message.answer("Пожалуйста, выбери из предложенных кнопок.")
    await state.update_data(level=message.text)
    await state.update_data(limitations=[])
    await Form.limitations.set()
    await message.answer("Выберите ограничения (по одному, нажмите 'Готово' когда закончите):", reply_markup=limitations_kb)

@dp.message_handler(state=Form.limitations)
async def process_limitations(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current = data.get("limitations", [])
    if message.text == "Готово":
        await state.update_data(limitations=current)
        await state.update_data(equipment=[])
        await Form.equipment.set()
        return await message.answer("Выберите инвентарь (по одному, нажмите 'Готово' когда закончите):", reply_markup=equipment_kb)
    elif message.text not in ["Грыжи", "Больные колени", "Ожирение", "Нет ограничений"]:
        return await message.answer("Пожалуйста, выбери из кнопок.")
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
    elif message.text not in ["Гантели", "Штанга", "Турник", "Резинки", "Нет"]:
        return await message.answer("Пожалуйста, выбери из кнопок.")
    if message.text not in current:
        current.append(message.text)
        await state.update_data(equipment=current)

@dp.message_handler(state=Form.duration)
async def process_duration(message: types.Message, state: FSMContext):
    if message.text not in ["15", "30", "45"]:
        return await message.answer("Пожалуйста, выбери из кнопок.")
    duration = int(message.text)
    await state.update_data(duration_minutes=duration)

    user_data = await state.get_data()
    await message.answer("Спасибо! Генерирую тренировку...", reply_markup=ReplyKeyboardRemove())

    workout = generate_workout(user_data)
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

if __name__ == '__main__':
    async def main():
        print("Bot started")
        await init_db()
        await dp.start_polling()

    asyncio.run(main())
