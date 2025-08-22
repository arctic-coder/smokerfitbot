import json
import os
from aiogram import types
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from yookassa.domain.exceptions.bad_request_error import BadRequestError


from states import Form
from utils import generate_workout
from db import get_user, save_user, get_subscription, set_free_workout_used, get_last_pending_payment_id, upsert_subscription
from keyboards import start_kb, level_kb, limitations_kb, equipment_kb, duration_kb
from constants import LEVELS, LIMITATIONS, EQUIPMENT, DURATION

from billing.service import (
    start_or_resume_checkout, check_and_activate, cancel_subscription, is_active
)

ADMIN_ID = int(os.getenv("ADMIN_ID", "0")) 

LEVELS_SET = set(LEVELS)                     
LIMITATIONS_SET = set(LIMITATIONS)          
EQUIPMENT_SET = set(EQUIPMENT)               
DURATION_SET = set(DURATION)  

def register_handlers(dp: Dispatcher) -> None:


    # --- email helpers ---
    import re
    from typing import Optional

    _EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

    def _valid_email(s: str) -> bool:
        return bool(_EMAIL_RE.match((s or "").strip()))

    def _extract_email_from_subscription_row(sub) -> Optional[str]:
        """
        Пока не жёстко задан индекс email в subscriptions — берём первое поле, похожее на e-mail.
        """
        if not sub:
            return None
        for x in sub:
            if isinstance(x, str) and "@" in x and " " not in x:
                return x
        return None

    # --- старт и выбор режима ---
    @dp.message_handler(commands='start', state="*")
    async def start_handler(message: types.Message, state: FSMContext):
        await state.finish()
            # 1) Разбираем deep-link аргумент к /start
        payload = message.get_args()  # вернёт строку после '?start='

        if payload == "payment_success":
            user_id = message.from_user.id

            # 2) Берём последний незавершённый платёж этого пользователя
            #    (по вашей логике их не может быть больше одного)
            from db import get_last_pending_payment_id, get_payment_confirmation_url
            payment_id = await get_last_pending_payment_id(user_id)

            if not payment_id:
                # Теоретически: пользователь уже всё завершил/отменил
                return await message.answer(
                    "Спасибо! Если вы завершили оплату — подписка будет активна. "
                    "Сейчас у вас нет неподтверждённых платежей. Команда: /status"
                )

            # 3) Пробуем подтянуть платёж из ЮKassa и при успехе активировать подписку
            from billing.service import check_and_activate
            try:
                result = await check_and_activate(user_id, payment_id)
            except Exception:
                # Здесь можно сделать более точную обработку, если внедрите YookassaNetworkError
                return await message.answer("Не получилось проверить платёж, попробуйте /check чуть позже.")

            if result == "succeeded":
                return await message.answer("Оплата прошла! Подписка активна ✅")
            elif result == "pending":
                # даём кнопку вернуться на страницу оплаты или отменить
                url = await get_payment_confirmation_url(payment_id)
                kb = InlineKeyboardMarkup()
                if url:
                    kb.add(InlineKeyboardButton("Вернуться к оплате", url=url))
                kb.add(InlineKeyboardButton("Отменить платёж", callback_data=f"cancelpay:{payment_id}"))
                return await message.answer("Платёж ещё не подтверждён. Нажмите /check чуть позже.", reply_markup=kb)
            else:
                return await message.answer("Платёж не прошёл или был отменён. Попробуйте /subscribe ещё раз.")

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
        from db import get_payment_confirmation_url, get_subscription
        user_id = message.from_user.id
        sub = await get_subscription(user_id)

        text_lines = []
        kb = InlineKeyboardMarkup()

        if not sub:
            text_lines.append("Статус: подписка не оформлена. Доступна 1 бесплатная тренировка.")
        else:
            status = sub[1]
            cpe = sub[3] or "-"
            nca = sub[4] or "-"
            text_lines.append(f"Статус подписки: {status}")
            text_lines.append(f"Доступ (оплачено) до: {cpe}")
            if status == "active":
                text_lines.append(f"Следующее списание: {nca} (≈ за 1 день до окончания)")

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

        # e-mail: берём из подписки или из state; если нет — просим ввести
        data = await state.get_data()
        sub_email = _extract_email_from_subscription_row(sub) or data.get("email")

        if not _valid_email(sub_email or ""):
            await state.update_data(next_flow="subscribe")
            await Form.email.set()
            return await message.answer("Введите e-mail для отправки чека:")

        # создать новый или возобновить pending и вернуть ссылку (передаём email!)
        try:
            payment_id, url = await start_or_resume_checkout(user_id, email=sub_email)
        except BadRequestError as e:
            return await message.answer(f"ЮKassa отклонила запрос: {getattr(e, 'description', 'invalid_request')}")
        except Exception:
            return await message.answer("Не удалось создать/возобновить платёж. Попробуйте позже.")

        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Перейти к оплате", url=url))
        kb.add(InlineKeyboardButton("Проверить оплату", callback_data=f"chkpay:{payment_id}"))
        kb.add(InlineKeyboardButton("Отменить платёж", callback_data=f"cancelpay:{payment_id}"))
        await message.answer("Оформление подписки: оплатите по ссылке ниже.", reply_markup=kb)


    @dp.message_handler(state=Form.email)
    async def process_email_for_subscription(message: types.Message, state: FSMContext):
        """
        Пользователь прислал e-mail → валидируем, сохраняем в подписке и запускаем создание/возобновление платежа.
        """
        user_id = message.from_user.id
        email = (message.text or "").strip()

        if not _valid_email(email):
            return await message.answer("Неверный e-mail. Введите корректный адрес:")

        # сохраняем e-mail в подписке (персист) + в state
        await upsert_subscription(user_id, email=email)
        await state.update_data(email=email)

        try:
            payment_id, url = await start_or_resume_checkout(user_id, email=email)
        except BadRequestError as e:
            await state.finish()
            return await message.answer(f"ЮKassa отклонила запрос: {getattr(e, 'description', 'invalid_request')}")
        except Exception:
            await state.finish()
            return await message.answer("Не удалось создать/возобновить платёж. Попробуйте позже.")

        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Перейти к оплате", url=url))
        kb.add(InlineKeyboardButton("Проверить оплату", callback_data=f"chkpay:{payment_id}"))
        kb.add(InlineKeyboardButton("Отменить платёж", callback_data=f"cancelpay:{payment_id}"))

        await message.answer("Отлично! Создал оплату, нажмите кнопку ниже:", reply_markup=kb)
        await state.finish()


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
    async def go_subscribe_cb(call: types.CallbackQuery, state: FSMContext):
        await call.answer()
        user_id = call.from_user.id

        sub = await get_subscription(user_id)
        if is_active(sub):
            cpe = sub[3] if sub else "-"
            cancelled_note = " (продление отключено)" if sub and sub[1] == "cancelled" else ""
            return await call.message.answer(f"У вас уже активная подписка{cancelled_note} ✅\nОплачено до: {cpe}")

        data = await state.get_data()
        sub_email = _extract_email_from_subscription_row(sub) or data.get("email")
        if not _valid_email(sub_email or ""):
            await state.update_data(next_flow="go_subscribe")
            await Form.email.set()
            return await call.message.answer("Введите e-mail для отправки чека:")

        try:
            payment_id, url = await start_or_resume_checkout(user_id, email=sub_email)
        except BadRequestError as e:
            return await call.message.answer(f"ЮKassa отклонила запрос: {getattr(e, 'description', 'invalid_request')}")
        except Exception:
            return await call.message.answer("Не удалось создать/возобновить платёж. Попробуйте позже.")

        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Перейти к оплате", url=url))
        kb.add(InlineKeyboardButton("Проверить оплату", callback_data=f"chkpay:{payment_id}"))
        kb.add(InlineKeyboardButton("Отменить платёж", callback_data=f"cancelpay:{payment_id}"))
        await call.message.answer("Оформление подписки: оплатите по ссылке ниже.", reply_markup=kb)



    @dp.callback_query_handler(lambda c: c.data.startswith("cancelpay:"), state="*")
    async def cancel_payment_cb(call: types.CallbackQuery, state: FSMContext):
        from db import upsert_payment_status
        await call.answer()
        payment_id = call.data.split(":", 1)[1]
        user_id = call.from_user.id

        # пометим платёж отменённым у себя
        await upsert_payment_status(user_id, payment_id, 0, "RUB", "canceled", raw_text='{"reason":"user_cancelled"}')

        # берём e-mail; если нет — просим пройти /subscribe, чтобы указать e-mail
        sub = await get_subscription(user_id)
        data = await state.get_data()
        sub_email = _extract_email_from_subscription_row(sub) or data.get("email")

        if not _valid_email(sub_email or ""):
            return await call.message.answer("Платёж отменён. Чтобы создать новый, отправьте /subscribe и укажите e-mail для чека.")

        try:
            new_id, url = await start_or_resume_checkout(user_id, email=sub_email)
        except Exception:
            return await call.message.answer("Не удалось создать новый платеж. Попробуйте позже.")

        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Перейти к оплате", url=url))
        kb.add(InlineKeyboardButton("Проверить оплату", callback_data=f"chkpay:{new_id}"))
        await call.message.answer("Текущий платёж отменён. Создан новый:", reply_markup=kb)



    #++++++ СЛУЖЕБНОЕ +++++++++++

    def _parse_local_datetime(s: str) -> datetime:
        """
        Принимает строки вида:
        - 'YYYY-MM-DD HH:MM'
        - 'YYYY-MM-DDTHH:MM'
        - 'YYYY-MM-DD HH:MM:SS'
        - 'YYYY-MM-DDTHH:MM:SS'
        Возвращает aware-datetime в Europe/Vienna.
        """
        s = s.strip().replace("T", " ")
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                dt_naive = datetime.strptime(s, fmt)
                return dt_naive.replace(tzinfo=ZoneInfo("Europe/Vienna"))
            except ValueError:
                continue
        raise ValueError("Неверный формат даты. Используй 'YYYY-MM-DD HH:MM'.")

    @dp.message_handler(commands='admin_next_charge', state="*")
    async def admin_next_charge_cmd(message: types.Message):
        """
        /admin_next_charge <user_id> <YYYY-MM-DD HH:MM>
        Пример: /admin_next_charge 197925837 2025-08-18 10:00
        Время интерпретируем как Europe/Vienna, сохраняем в БД в UTC (ISO-строка).
        """
        if message.from_user.id != ADMIN_ID:
            return await message.answer("Недостаточно прав.")

        try:
            # Разбираем аргументы
            parts = message.text.strip().split(maxsplit=2)
            if len(parts) < 3:
                raise ValueError("Нужно 2 аргумента: <user_id> <YYYY-MM-DD HH:MM>")

            uid_str, dt_str = parts[1], parts[2]
            uid = int(uid_str)

            # Парсим локальное время и конвертируем в UTC
            local_dt = _parse_local_datetime(dt_str)
            utc_dt = local_dt.astimezone(timezone.utc)

            # Пишем в БД ИМЕННО ISO-строкой 
            await upsert_subscription(uid, next_charge_at=utc_dt.isoformat())

            # Читаем обратно, чтобы показать, что реально лежит
            sub = await get_subscription(uid)
            stored_nca = sub[4] if sub else None  # (user_id, status, payment_method_id, current_period_end, next_charge_at, ...)
            try:
                stored_utc = datetime.fromisoformat(stored_nca).replace(tzinfo=timezone.utc)
                stored_local = stored_utc.astimezone(ZoneInfo("Europe/Vienna")).strftime("%Y-%m-%d %H:%M")
            except Exception:
                stored_local = str(stored_nca)

            return await message.answer(
                f"OK: next_charge_at для {uid} → {utc_dt.isoformat()} (UTC)\n"
                f"= {stored_local} (Europe/Vienna) — сохранено."
            )
        except Exception as e:
            return await message.answer(
                f"Ошибка: {e}\n"
                "Пример: /admin_next_charge 197925837 2025-08-18 10:00"
            )
