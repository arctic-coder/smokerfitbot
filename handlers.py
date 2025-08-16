import json
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from yookassa.domain.exceptions.bad_request_error import BadRequestError


from states import Form
from utils import generate_workout
from db import get_user, save_user, get_subscription, set_free_workout_used
from keyboards import start_kb, level_kb, limitations_kb, equipment_kb, duration_kb
from constants import LEVELS, LIMITATIONS, EQUIPMENT, DURATION_MINUTES

from billing.service import (
    start_subscription, check_and_activate, cancel_subscription, is_active
)

# множества для быстрых проверок
LEVELS_SET = set(LEVELS)                      # строки
LIMITATIONS_SET = set(LIMITATIONS)            # строки (включая "Нет ограничений")
EQUIPMENT_SET = set(EQUIPMENT)                # строки (включая "Ничего")
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

        # users: (user_id, level, limitations, equipment, duration_minutes, free_workout_used, email, phone)
        level = row[1]
        limitations_json = row[2]
        equipment_json = row[3]

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

        # --- доступ: free + подписка ---
        user_id = message.from_user.id
        sub = await get_subscription(user_id)
        user_row = await get_user(user_id)
        free_used = False
        if user_row and len(user_row) >= 6:
            free_used = bool(user_row[5])

        if not is_active(sub):
            if not free_used:
                # даём бесплатную попытку и помечаем
                await set_free_workout_used(user_id, True)
            else:
                # показываем пейволл
                pay_kb = InlineKeyboardMarkup().add(
                    InlineKeyboardButton("Оформить подписку", callback_data="go_subscribe")
                )
                await message.answer(
                    "Бесплатная тренировка уже использована.\nОформите подписку, чтобы продолжить.",
                    reply_markup=pay_kb
                )
                return  # выходим до генерации

        # --- генерация ---
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
            user_id=user_id,
            level=user_data['level'],
            limitations=user_data['limitations'],
            equipment=user_data['equipment'],
            duration_minutes=user_data['duration_minutes']
        )
        await state.finish()

    # --- команды подписки
    @dp.message_handler(commands='status', state="*")
    async def status_cmd(message: types.Message):
        sub = await get_subscription(message.from_user.id)
        if not sub:
            return await message.answer("Статус: нет активной подписки. Доступна 1 бесплатная тренировка.")
        status = sub[1]
        cpe = sub[3]
        await message.answer(f"Статус подписки: {status}\nОплачено до: {cpe or '-'}")

    @dp.message_handler(commands='cancel', state="*")
    async def cancel_cmd(message: types.Message):
        await cancel_subscription(message.from_user.id)
        await message.answer("Подписка отменена. Вы можете оформить её снова в любой момент: /subscribe")

    @dp.message_handler(commands='subscribe', state="*")
    async def subscribe_cmd(message: types.Message, state: FSMContext):
        try:
            payment_id, url = await start_subscription(message.from_user.id, email=None, phone=None)
        except BadRequestError as e:
            # Покажем описание ошибки из ЮKassa
            await message.answer(f"ЮKassa отклонила запрос: {getattr(e, 'description', 'invalid_request')}")
            return
        except Exception as e:
            await message.answer("Не удалось создать платёж. Попробуйте позже.")
            return

        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Перейти к оплате", url=url))
        kb.add(InlineKeyboardButton("Проверить оплату", callback_data=f"chkpay:{payment_id}"))
        await message.answer("Оформление подписки: оплатите по ссылке ниже.", reply_markup=kb)


    # --- колбэки 
    @dp.callback_query_handler(lambda c: c.data and c.data.startswith("chkpay:"), state="*")
    async def check_payment_cb(call: types.CallbackQuery):
        await call.answer()  # закрыть "крутилку"
        payment_id = call.data.split(":", 1)[1]
        ok = await check_and_activate(call.from_user.id, payment_id)
        if ok:
            await call.message.edit_text("Оплата прошла! Подписка активна ✅")
        else:
            await call.answer("Платёж пока не подтверждён", show_alert=True)

    @dp.callback_query_handler(lambda c: c.data == "go_subscribe", state="*")
    async def go_subscribe_cb(call: types.CallbackQuery):
        await call.answer()
        try:
            payment_id, url = await start_subscription(call.from_user.id, email=None, phone=None)
        except BadRequestError as e:
            await call.message.answer(f"ЮKassa отклонила запрос: {getattr(e, 'description', 'invalid_request')}")
            return
        except Exception:
            await call.message.answer("Не удалось создать платёж. Попробуйте позже.")
            return

        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Перейти к оплате", url=url))
        kb.add(InlineKeyboardButton("Проверить оплату", callback_data=f"chkpay:{payment_id}"))
        await call.message.answer("Оформление подписки: оплатите по ссылке ниже.", reply_markup=kb)

