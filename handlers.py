import json
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from yookassa.domain.exceptions.bad_request_error import BadRequestError


from states import Form
from utils import generate_workout
from db import get_user, save_user, get_subscription, set_free_workout_used, get_last_pending_payment_id
from keyboards import start_kb, level_kb, limitations_kb, equipment_kb, duration_kb
from constants import LEVELS, LIMITATIONS, EQUIPMENT, DURATION

from billing.service import (
    start_or_resume_checkout, start_subscription, check_and_activate, cancel_subscription, is_active
)

# множества для быстрых проверок
LEVELS_SET = set(LEVELS)                     
LIMITATIONS_SET = set(LIMITATIONS)          
EQUIPMENT_SET = set(EQUIPMENT)               
DURATION_SET = set(DURATION)  

def register_handlers(dp: Dispatcher) -> None:

    # --- старт и выбор режима ---
    @dp.message_handler(commands='start', state="*")
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
        await message.answer("Какой у вас опыт регулярных занятий силовыми?", reply_markup=level_kb)

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

        await state.update_data(duration_minutes=message.text)

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

    @dp.message_handler(commands='status', state="*")
    async def status_cmd(message: types.Message):
        from db import get_payment_confirmation_url
        user_id = message.from_user.id
        sub = await get_subscription(user_id)

        text_lines = []
        kb = InlineKeyboardMarkup()

        if not sub:
            text_lines.append("Статус: подписка не оформлена. Доступна 1 бесплатная тренировка.")
        else:
            status = sub[1]
            cpe = sub[3] or "-"
            text_lines.append(f"Статус подписки: {status}")
            text_lines.append(f"Доступ (оплачено) до: {cpe}")

        pending_id = await get_last_pending_payment_id(user_id)
        if pending_id:
            url = await get_payment_confirmation_url(pending_id)
            if url:
                kb.add(InlineKeyboardButton("Вернуться к оплате", url=url))
            kb.add(InlineKeyboardButton("Проверить оплату", callback_data=f"chkpay:{pending_id}"))
            kb.add(InlineKeyboardButton("Отменить платёж", callback_data=f"cancelpay:{pending_id}"))
            text_lines.append("\nЕсть незавершённый платёж.")

        text_lines.append("\nКоманды: /subscribe — оформить, /check — проверить, /cancel — отключить продление")
        await message.answer("\n".join(text_lines), reply_markup=kb if kb.inline_keyboard else None)


    @dp.message_handler(commands='cancel', state="*")
    async def cancel_cmd(message: types.Message):
        sub = await get_subscription(message.from_user.id)
        if not sub:
            return await message.answer("Подписка не оформлена.")

        # sub: (user_id, status, payment_method_id, current_period_end, ...)
        status, cpe = sub[1], sub[3]
        if not cpe:
            return await message.answer("Подписка не активна.")

        # уже отменена?
        if status == "cancelled":
            return await message.answer(f"Продление уже отключено. Доступ — до {cpe}.")

        # спросим подтверждение
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Да, отменить продление", callback_data="cancel_yes"),
            InlineKeyboardButton("Оставить как есть", callback_data="cancel_no"),
        )
        await message.answer(
            f"Вы уверены, что хотите отменить продление? Доступ сохранится до {cpe}.",
            reply_markup=kb
        )

    @dp.callback_query_handler(lambda c: c.data == "cancel_yes", state="*")
    async def cancel_yes_cb(call: types.CallbackQuery):
        await call.answer()
        await cancel_subscription(call.from_user.id)
        await call.message.edit_text("Продление отключено. Доступ сохранится до конца оплаченного периода. /status")

    @dp.callback_query_handler(lambda c: c.data == "cancel_no", state="*")
    async def cancel_no_cb(call: types.CallbackQuery):
        await call.answer("Оставили как есть ✅", show_alert=False)



    @dp.message_handler(commands='subscribe', state="*")
    async def subscribe_cmd(message: types.Message, state: FSMContext):
        user_id = message.from_user.id

        sub = await get_subscription(user_id)
        if is_active(sub):
            cpe = sub[3] if sub else "-"
            cancelled_note = " (продление отключено)" if sub and sub[1] == "cancelled" else ""
            return await message.answer(
                f"У вас уже активная подписка{cancelled_note} ✅\nОплачено до: {cpe}\n\n"
                "Продление будет доступно ближе к дате окончания. Команда: /status"
            )

        # создать новый или возобновить pending и вернуть ссылку
        try:
            payment_id, url = await start_or_resume_checkout(user_id, email=None, phone=None)
        except BadRequestError as e:
            return await message.answer(f"ЮKassa отклонила запрос: {getattr(e, 'description', 'invalid_request')}")
        except Exception:
            return await message.answer("Не удалось создать/возобновить платёж. Попробуйте позже.")

        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Перейти к оплате", url=url))
        kb.add(InlineKeyboardButton("Проверить оплату", callback_data=f"chkpay:{payment_id}"))
        kb.add(InlineKeyboardButton("Отменить платёж", callback_data=f"cancelpay:{payment_id}"))
        await message.answer("Оформление подписки: оплатите по ссылке ниже.", reply_markup=kb)

    @dp.message_handler(commands='check', state="*")
    async def check_cmd(message: types.Message):
        from db import get_payment_confirmation_url
        payment_id = await get_last_pending_payment_id(message.from_user.id)
        if not payment_id:
            return await message.answer("Нет платежей, ожидающих подтверждения. Используйте /subscribe, чтобы оформить подписку.")

        try:
            result = await check_and_activate(message.from_user.id, payment_id)
        except BadRequestError as e:
            return await message.answer(f"ЮKassa отклонила запрос: {getattr(e, 'description', 'invalid_request')}")

        if result == "succeeded":
            await message.answer("Оплата прошла! Подписка активна ✅")
        elif result == "pending":
            url = await get_payment_confirmation_url(payment_id)
            kb = InlineKeyboardMarkup()
            if url:
                kb.add(InlineKeyboardButton("Вернуться к оплате", url=url))
            kb.add(InlineKeyboardButton("Отменить платёж", callback_data=f"cancelpay:{payment_id}"))
            await message.answer("Платёж ещё не подтверждён. Если вы оплатили — подождите минуту и нажмите /check снова.", reply_markup=kb)
        else:
            await message.answer("Платёж не прошёл или был отменён. Попробуйте /subscribe ещё раз.")


    # --- колбэки 
    @dp.callback_query_handler(lambda c: c.data and c.data.startswith("chkpay:"), state="*")
    async def check_payment_cb(call: types.CallbackQuery):
        from db import get_payment_confirmation_url
        await call.answer()
        payment_id = call.data.split(":", 1)[1]
        try:
            result = await check_and_activate(call.from_user.id, payment_id)
        except BadRequestError as e:
            return await call.message.answer(f"ЮKassa отклонила запрос: {getattr(e, 'description', 'invalid_request')}")

        if result == "succeeded":
            await call.message.edit_text("Оплата прошла! Подписка активна ✅")
        elif result == "pending":
            url = await get_payment_confirmation_url(payment_id)
            kb = InlineKeyboardMarkup()
            if url:
                kb.add(InlineKeyboardButton("Вернуться к оплате", url=url))
            kb.add(InlineKeyboardButton("Отменить платёж", callback_data=f"cancelpay:{payment_id}"))
            await call.message.answer("Платёж ещё не подтверждён. Если вы оплатили — подождите минуту и нажмите ещё раз.", reply_markup=kb)
        else:
            await call.message.answer("Платёж не прошёл или был отменён. Попробуйте /subscribe ещё раз.")


    @dp.callback_query_handler(lambda c: c.data == "go_subscribe", state="*")
    async def go_subscribe_cb(call: types.CallbackQuery):
        await call.answer()
        user_id = call.from_user.id

        sub = await get_subscription(user_id)
        if is_active(sub):
            cpe = sub[3] if sub else "-"
            cancelled_note = " (продление отключено)" if sub and sub[1] == "cancelled" else ""
            return await call.message.answer(f"У вас уже активная подписка{cancelled_note} ✅\nОплачено до: {cpe}")

        try:
            payment_id, url = await start_or_resume_checkout(user_id, email=None, phone=None)
        except BadRequestError as e:
            return await call.message.answer(f"ЮKassa отклонила запрос: {getattr(e, 'description', 'invalid_request')}")
        except Exception:
            return await call.message.answer("Не удалось создать/возобновить платёж. Попробуйте позже.")

        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Перейти к оплате", url=url))
        kb.add(InlineKeyboardButton("Проверить оплату", callback_data=f"chkpay:{payment_id}"))
        kb.add(InlineKeyboardButton("Отменить платёж", callback_data=f"cancelpay:{payment_id}"))
        await call.message.answer("Оформление подписки: оплатите по ссылке ниже.", reply_markup=kb)



    @dp.callback_query_handler(lambda c: c.data.startswith("cancelpay:"), state="*")
    async def cancel_payment_cb(call: types.CallbackQuery):
        from db import upsert_payment_status
        await call.answer()
        payment_id = call.data.split(":", 1)[1]
        user_id = call.from_user.id

        # пометим платёж отменённым у себя
        await upsert_payment_status(user_id, payment_id, 0, "RUB", "canceled", raw_text='{"reason":"user_cancelled"}')

        # запустим обычный флоу — создадим новый или вернём ссылку на другой pending
        try:
            new_id, url = await start_or_resume_checkout(user_id, email=None, phone=None)
        except Exception:
            return await call.message.answer("Не удалось создать новый платеж. Попробуйте позже.")

        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Перейти к оплате", url=url))
        kb.add(InlineKeyboardButton("Проверить оплату", callback_data=f"chkpay:{new_id}"))
        await call.message.answer("Текущий платёж отменён. Создан новый:", reply_markup=kb)




