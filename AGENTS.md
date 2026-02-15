# AGENTS.md — SmokerFitBot

## Project overview

SmokerFitBot is a Telegram bot for personalized fitness coaching (Python 3.10, aiogram 2.25.2) with integrated recurring billing via Yookassa. Users fill a fitness profile (level, limitations, equipment, duration) and receive generated workouts. The bot runs on PostgreSQL (asyncpg), uses aiohttp for payment webhooks, and has a background autobiller for recurring charges.

## Tech stack

- **Language:** Python 3.10.13
- **Bot framework:** aiogram 2.25.2 (async Telegram Bot API)
- **Database:** PostgreSQL via asyncpg connection pool
- **Payments:** Yookassa SDK 3.3.0
- **HTTP server:** aiohttp (webhooks on port 8080)
- **Config:** python-dotenv, dataclass-based `Config`

## Architecture

```
main.py              — entry point: inits DB, bot, webhook server, autobiller
config.py            — Config dataclass from env vars
db.py                — all SQL queries, connection pool, schema init (~620 LOC)
states.py            — aiogram FSM states for conversation flow
keyboards.py         — Telegram InlineKeyboard definitions
texts.py             — all user-facing strings (Russian)
utils.py             — workout generation and exercise filtering

handlers/            — Telegram message/callback handlers
  common.py          — /start, /help, profile display
  form.py            — user profile form FSM
  subscription.py    — subscription purchase flow

billing/
  service.py         — subscription business logic (activate, charge, cancel)
  yookassa_client.py — Yookassa API wrapper (create payment, recurring charge)

jobs/
  autobiller.py      — background loop: precharge notify, auto-charge, retries

web/
  yk_handlers.py     — POST /yookassa/webhook handler

scripts/             — one-off data migration (Excel → JSON → SQL)
data/                — exercises.json, exercises_sql.sql
tests/               — pytest async tests for billing logic
```

## Database

PostgreSQL with 5 tables: `users`, `subscriptions`, `payments`, `exercises`, `promocodes`. Schema is created in `db.init_db()`. All queries are raw SQL in `db.py` — there is no ORM.

Key patterns:
- Upsert via `ON CONFLICT ... DO UPDATE`
- JSONB for exercise equipment alternatives (`equipment_dnf`)
- `TEXT[]` arrays with GIN indexes for exercise filtering
- Timestamps stored as naive UTC (`TIMESTAMP WITHOUT TIME ZONE`)

## Running

```bash
pip install -r requirements.txt
# configure .env (see .env.example)
python main.py
```

The bot uses long-polling (not webhook) for Telegram. The aiohttp server on :8080 handles only Yookassa webhooks and `/healthz`.

## Testing

```bash
docker-compose -f docker-compose.test.yml up -d db   # start test PostgreSQL
DATABASE_URL=postgresql://... pytest tests/ -v
```

Tests use `asyncio` + `unittest.mock`. Fixtures in `tests/conftest.py` set up a real PostgreSQL database. Tests cover autobiller, precharge notifications, and retry logic.

## Key conventions

- All user-facing text is in `texts.py` (Russian language)
- Prices are in kopeks (integer cents). Month=35000, Year=190000
- Logging via stdlib `logging`; setup in `logging_setup.py`
- No type checker or linter configured (only Bandit for security scanning in CI)
- No ORM — all DB access is raw asyncpg queries in `db.py`
- Async everywhere — all handlers, DB calls, and billing logic are async/await

## Common tasks

- **Add a new handler:** create function in `handlers/`, register in `handlers/__init__.py`
- **Add a DB query:** add async function in `db.py` using `acquire_conn()` context manager
- **Change pricing/text:** edit `texts.py` for copy, env vars for prices
- **Add exercise data:** use `scripts/export_exercises_to_json.py` → `scripts/json_to_sql.py`
- **Test billing changes:** write async tests in `tests/`, mock Yookassa client

## Gotchas

- `db.py` uses a module-level global `pool` variable — tests must call `init_db()` first
- aiogram v2 (not v3) — handler registration uses decorators or `dp.register_*`
- `.env` is gitignored; `.env.example` has the template
- `data/` directory is gitignored — exercise data must be imported via scripts
- Yookassa webhooks expect raw JSON body; `client_max_size` is configurable
