# Implementation Plan: Tests + Linter + Type Hints + aiogram v3 Migration

## Phase Order

1. **Linter/formatter config** — low risk, gives us formatting for all subsequent work
2. **aiogram v3 migration** — biggest structural change, must come before typing/tests
3. **Type hints** — annotate final v3 code (no point typing code about to be rewritten)
4. **More tests** — test the final v3 codebase

Tests run after every phase. Existing 3 test files must pass throughout.

---

## Phase 1: Linter/Formatter Config

### 1.1 Create `pyproject.toml`
- ruff config: target-version="py310", line-length=120
- Select rules: E, W, F, I, UP, B, SIM, RUF
- Ignore: E501, B008, RUF001/2/3 (Russian unicode)
- isort known-first-party for local modules
- pytest config: asyncio_mode="auto", testpaths=["tests"]

### 1.2 Create `requirements-dev.txt`
- ruff, pytest, pytest-asyncio

### 1.3 Run `ruff check --fix .` and `ruff format .`
Known fixes:
- `main.py:31` — semicolon after `Config.from_env();`
- `main.py:1` — `import logging, os` split
- Import sorting across all files
- Trailing whitespace cleanup
- `billing/service.py:328-332` — indentation fix in `if notifier` block

### 1.4 Run tests → all must pass

---

## Phase 2: aiogram v2 → v3 Migration

Target: **aiogram 3.15.0** (latest stable)

### 2.1 Update `requirements.txt`
```
aiogram==3.15.0
python-dotenv==1.0.0
asyncpg
yookassa==3.3.0
aiohttp
```
Remove `aiosqlite` (unused).

### 2.2 `states.py` — import change only
```python
# OLD: from aiogram.dispatcher.filters.state import State, StatesGroup
# NEW: from aiogram.fsm.state import State, StatesGroup
```

### 2.3 `keyboards.py` — constructor changes
- `ReplyKeyboardMarkup`: no more `.row()`. Use `keyboard=[[KeyboardButton(text=...)]]`
- `InlineKeyboardMarkup`: no more `.add()`. Use `inline_keyboard=[[btn, ...]]`
- Import `KeyboardButton`
- Rewrite `_mk()` helper, all `kb_*` functions

### 2.4 `handlers/__init__.py` — Router pattern
```python
from aiogram import Router
from .common import common_router
from .form import form_router
from .subscription import subscription_router

def get_main_router() -> Router:
    router = Router()
    router.include_router(common_router)
    router.include_router(form_router)
    router.include_router(subscription_router)
    return router
```

### 2.5 `handlers/common.py`
- Use `Router` + decorators
- `CommandStart` filter provides `command.args` (replaces `message.get_args()`)
- `await state.finish()` → `await state.clear()`
- Extract `send_start_screen()` helper for cross-handler use
- `StateFilter("*")` for any-state handlers

### 2.6 `handlers/form.py`
- `Router` + decorators
- `F.text == BTN_FILL_FORM` replaces lambda filters
- All 7 state transitions: `await Form.X.set()` → `await state.set_state(Form.X)`
- `await state.finish()` → `await state.clear()`
- Remove `register_form_handlers(dp)` — replaced by `form_router`

### 2.7 `handlers/subscription.py`
- `Router` + decorators
- Lambda callback filters → `F.data.startswith(...)` / `F.data == ...`
- `await Form.email.set()` → `await state.set_state(Form.email)`
- `await state.finish()` → `await state.clear()`
- Line 285 `InlineKeyboardMarkup().add(...)` → `InlineKeyboardMarkup(inline_keyboard=[[...]])`
- Replace 3 calls to `start_cmd(call.message, state)` with `send_start_screen(call.message, state)`
- `status_cmd`: always pass keyboard (no empty constructor check)
- Remove `register_subscription_handlers(dp)`

### 2.8 `main.py`
- `from aiogram.fsm.storage.memory import MemoryStorage`
- `dp = Dispatcher(storage=MemoryStorage())` (no bot arg)
- `dp.include_router(get_main_router())`
- `await dp.start_polling(bot)` (bot passed here now)

### 2.9 Files unchanged in this phase
- `config.py`, `db.py`, `texts.py`, `utils.py`
- `billing/service.py`, `billing/yookassa_client.py`
- `jobs/autobiller.py`, `web/yk_handlers.py`, `logging_setup.py`

### 2.10 Run tests → existing 3 test files must still pass
(They mock billing.service and db — no aiogram imports — should work unchanged.)

---

## Phase 3: Type Hints

Add return type + parameter annotations to all public functions.

### 3.1 `db.py`
- `save_user(user_id: int, level: str, limitations: list[str], ...) -> None`
- `get_user(user_id: int) -> tuple[int, str, str, str, str, bool, str] | None`
- `get_subscription(user_id: int) -> tuple[...] | None`
- `upsert_subscription(user_id: int, **fields: Any) -> None`
- All other functions: add missing return types
- `_parse_iso`, `_to_pg_timestamp`, `_ensure_eqdnf` — annotate parameters

### 3.2 `utils.py`
- `_equipment_options_ok(user_eq: list[str], options: list[list[str]]) -> bool`
- `generate_workout(user_data: dict[str, Any]) -> list[dict[str, Any]]`

### 3.3 `billing/service.py`
- `check_and_activate(user_id: int, payment_id: str) -> str`
- `cancel_subscription(user_id: int) -> None`
- `start_or_resume_checkout(...) -> tuple[str, str | None]`
- `charge_recurring(user_id: int, notifier: Notifier = None) -> str`
- `charge_due_subscriptions(notifier: Notifier = None) -> dict[str, int]`
- Helper functions: annotate parameters

### 3.4 `billing/yookassa_client.py`
- `_make_receipt(email: str | None, amount_value: str, title: str) -> dict[str, Any]`
- `create_checkout_payment(...) -> tuple[str, str | None]`
- `create_recurring_payment(...) -> Any` (Yookassa Payment object)
- `get_payment(payment_id: str) -> Any`

### 3.5 Other files
- `keyboards.py` — return types for all `kb_*` functions
- `texts.py` — `_fmt_rub`, `start_sub_month_label`, `start_sub_year_label`
- Handler files — already typed from v3 migration
- `logging_setup.py`, `config.py` — already typed

### 3.6 Run tests → all must pass

---

## Phase 4: More Tests

### 4.1 Update `tests/conftest.py`
- Add helper fixtures: `make_message()`, `make_callback()`, `make_state()`
- These create MagicMock objects for aiogram Message, CallbackQuery, FSMContext

### 4.2 `tests/test_utils.py` — workout generation
- Pure function tests for `_level_ok`, `_limitations_ok`, `_equipment_options_ok`
- Integration tests for `generate_workout()` with seeded exercises in DB
- Test all 3 durations: 5-10 (1 set), 15-20 (2 sets), 35-45 (4 sets / 3+2 with extras)
- Edge case: empty result when no matching exercises

### 4.3 `tests/test_db.py` — database query integration tests
- `save_user` + `get_user` roundtrip
- `upsert_subscription` + `get_subscription`
- Payment lifecycle: `upsert_payment_status`, `get_last_pending_payment_id`, `mark_payment_applied` (idempotent)
- `cancel_other_pendings`
- Promocode lifecycle: `has_active_promocodes`, `get_active_promocode` (case-insensitive)
- `list_due_subscriptions` with time-based filtering
- `list_precharge_subscriptions`

### 4.4 `tests/test_handlers_common.py`
- `help_cmd` → sends HELP text
- `start_cmd` with no payload → sends START_MESSAGE
- `start_cmd` with `payment_success` deep link → checks payment flow
- `send_start_screen` helper

### 4.5 `tests/test_handlers_form.py`
- `_to_list()` pure function tests (None, list, JSON string, plain string)
- Form flow: `fill_form_new` → sets Form.level state
- `level_step` valid/invalid input
- `limitations_step` with BTN_DONE, valid selection, BTN_LIMIT_NO toggle
- `equipment_step` with BTN_DONE, BTN_EQUIP_NONE toggle
- `duration_step` — subscription check branching

### 4.6 `tests/test_handlers_subscription.py`
- `subscribe_cmd` with/without active subscription
- `subscribe_cb` callback
- `process_promo_code` valid/invalid promo
- `cancel_cmd` / `cancel_yes_cb`
- `process_email_for_subscription` valid/invalid email
- `check_payment_cb` succeeded/pending/failed
- `is_active()` with future/past cpe, various statuses

### 4.7 `tests/test_webhook.py`
- Bad JSON → 400
- Valid payment event → calls check_and_activate, returns 200
- Unknown payment_id → returns 200 (no crash)

### 4.8 `tests/test_billing_service.py`
- `_calc_renewal_dates` with future cpe / expired cpe
- `_next_month` edge cases (Jan 31 → Feb 28)
- `is_active` with all status/cpe combinations
- `_extract_email_from_subscription_row`

### 4.9 Run full test suite → all pass
