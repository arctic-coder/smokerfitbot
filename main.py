from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv
import os

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer("Привет! Я — Конструктор тренировок от Физкультуры курильщика 🏋️‍♀️\nНапиши /go чтобы начать.")

@dp.message_handler(commands=['go'])
async def go_handler(message: types.Message):
    await message.answer("Какой у вас уровень подготовки?\n\n1️⃣ Новичок\n2️⃣ 1–2 года\n3️⃣ 3+ лет\n(пока только тестируем!)")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True) #start endless cycle waiting for input