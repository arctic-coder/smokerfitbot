import os
import json
import aiosqlite
import asyncpg
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"
DB_PATH = os.getenv("SQLITE_PATH", "user_data.db")
PG_DSN = os.getenv("DATABASE_URL")

# ---------- helpers ----------
def _now_iso() -> str:
    return datetime.utcnow().isoformat()

# ---------- USERS ----------
async def _init_users_sqlite(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            level TEXT,
            limitations TEXT,          -- JSON (list[str])
            equipment TEXT,            -- JSON (list[str])
            duration_minutes INTEGER,
            free_workout_used INTEGER DEFAULT 0,  -- 0/1
            email TEXT,
            phone TEXT
        )
    """)
    await conn.commit()

async def _init_users_pg(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            level TEXT,
            limitations TEXT,
            equipment TEXT,
            duration_minutes INTEGER,
            free_workout_used BOOLEAN DEFAULT FALSE,
            email TEXT,
            phone TEXT
        )
    """)

async def save_user(user_id, level, limitations, equipment, duration_minutes):
    lim_json = json.dumps(limitations or [])
    eq_json  = json.dumps(equipment or [])
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO users (user_id, level, limitations, equipment, duration_minutes)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    level = excluded.level,
                    limitations = excluded.limitations,
                    equipment = excluded.equipment,
                    duration_minutes = excluded.duration_minutes
            """, (user_id, level, lim_json, eq_json, duration_minutes))
            await db.commit()
    else:
        conn = await asyncpg.connect(PG_DSN)
        await conn.execute("""
            INSERT INTO users (user_id, level, limitations, equipment, duration_minutes)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id) DO UPDATE SET
                level = EXCLUDED.level,
                limitations = EXCLUDED.limitations,
                equipment = EXCLUDED.equipment,
                duration_minutes = EXCLUDED.duration_minutes
        """, user_id, level, lim_json, eq_json, duration_minutes)
        await conn.close()


async def get_user(user_id):
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
                return await cur.fetchone()
    else:
        conn = await asyncpg.connect(PG_DSN)
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        await conn.close()
        if row:
            return (row["user_id"], row["level"], row["limitations"], row["equipment"],
                    row["duration_minutes"], row["free_workout_used"], row["email"], row["phone"])
        return None

async def set_free_workout_used(user_id: int, used: bool = True):
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO users (user_id, free_workout_used)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    free_workout_used = excluded.free_workout_used
            """, (user_id, 1 if used else 0))
            await db.commit()
    else:
        conn = await asyncpg.connect(PG_DSN)
        await conn.execute("""
            INSERT INTO users (user_id, free_workout_used)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE SET
                free_workout_used = EXCLUDED.free_workout_used
        """, user_id, used)
        await conn.close()


# ---------- SUBSCRIPTIONS ----------
# statuses: trial | active | past_due | cancelled
async def _init_subscriptions_sqlite(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            status TEXT,
            payment_method_id TEXT,
            current_period_end TEXT,
            next_charge_at TEXT,
            amount INTEGER,
            currency TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    await conn.commit()

async def _init_subscriptions_pg(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id BIGINT PRIMARY KEY,
            status TEXT,
            payment_method_id TEXT,
            current_period_end TIMESTAMP,
            next_charge_at TIMESTAMP,
            amount INTEGER,
            currency TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)

async def upsert_subscription(user_id: int, **fields):
    now = _now_iso()
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            # прочитать текущую
            async with db.execute("SELECT user_id FROM subscriptions WHERE user_id = ?", (user_id,)) as cur:
                exists = await cur.fetchone()
            if exists:
                # динамический апдейт
                cols = ", ".join([f"{k} = ?" for k in fields.keys()])
                vals = list(fields.values()) + [now, user_id]
                await db.execute(f"UPDATE subscriptions SET {cols}, updated_at = ? WHERE user_id = ?", vals)
            else:
                cols = ", ".join(["user_id"] + list(fields.keys()) + ["created_at", "updated_at"])
                placeholders = ", ".join(["?"] * (1 + len(fields) + 2))
                vals = [user_id] + list(fields.values()) + [now, now]
                await db.execute(f"INSERT INTO subscriptions ({cols}) VALUES ({placeholders})", vals)
            await db.commit()
    else:
        conn = await asyncpg.connect(PG_DSN)
        # соберём апсерт через ON CONFLICT
        cols = list(fields.keys())
        vals = list(fields.values())
        set_clause = ", ".join([f"{c} = EXCLUDED.{c}" for c in cols] + ["updated_at = EXCLUDED.updated_at"])
        await conn.execute(f"""
            INSERT INTO subscriptions (user_id, {", ".join(cols)}, created_at, updated_at)
            VALUES ($1, {", ".join(f"${i+2}" for i in range(len(vals)))}, NOW(), NOW())
            ON CONFLICT (user_id) DO UPDATE SET {set_clause}
        """, user_id, *vals)
        await conn.close()

async def get_subscription(user_id: int):
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,)) as cur:
                return await cur.fetchone()
    else:
        conn = await asyncpg.connect(PG_DSN)
        row = await conn.fetchrow("SELECT * FROM subscriptions WHERE user_id = $1", user_id)
        await conn.close()
        if row:
            return (
                row["user_id"], row["status"], row["payment_method_id"],
                row["current_period_end"], row["next_charge_at"],
                row["amount"], row["currency"], row["created_at"], row["updated_at"]
            )
        return None

# ---------- PAYMENTS (audit) ----------
async def _init_payments_sqlite(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            payment_id TEXT,
            amount INTEGER,
            currency TEXT,
            status TEXT,
            created_at TEXT,
            raw TEXT
        )
    """)
    await conn.commit()

async def _init_payments_pg(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            payment_id TEXT,
            amount INTEGER,
            currency TEXT,
            status TEXT,
            created_at TIMESTAMP,
            raw TEXT
        )
    """)

async def insert_payment(user_id: int, payment_id: str, amount: int, currency: str, status: str, raw_text: str):
    now = _now_iso()
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO payments (user_id, payment_id, amount, currency, status, created_at, raw)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, payment_id, amount, currency, status, now, raw_text))
            await db.commit()
    else:
        conn = await asyncpg.connect(PG_DSN)
        await conn.execute("""
            INSERT INTO payments (user_id, payment_id, amount, currency, status, created_at, raw)
            VALUES ($1, $2, $3, $4, $5, NOW(), $6)
        """, user_id, payment_id, amount, currency, status, raw_text)
        await conn.close()

# ---------- EXERCISES (как было) ----------
async def _init_exercises_sqlite(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            levels TEXT,
            equipment TEXT,
            equipment_dnf TEXT,
            allowed_limitations TEXT,
            muscle_group TEXT,
            reps_note TEXT,
            video_url TEXT
        )
    """)
    await conn.commit()

async def _init_exercises_pg(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            levels TEXT[],
            equipment TEXT[],
            equipment_dnf JSONB,
            allowed_limitations TEXT[],
            muscle_group TEXT,
            reps_note TEXT,
            video_url TEXT
        )
    """)

# -------- init all --------
async def init_db():
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as conn:
            await _init_users_sqlite(conn)
            await _init_subscriptions_sqlite(conn)
            await _init_payments_sqlite(conn)
            await _init_exercises_sqlite(conn)
    else:
        conn = await asyncpg.connect(PG_DSN)
        await _init_users_pg(conn)
        await _init_subscriptions_pg(conn)
        await _init_payments_pg(conn)
        await _init_exercises_pg(conn)
        await conn.close()
