import os
import json
import aiosqlite
import asyncpg
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"
DB_PATH = os.getenv("SQLITE_PATH", "user_data.db")
PG_DSN = os.getenv("DATABASE_URL")

# ---------- helpers ----------
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _to_pg_timestamp(v) -> datetime | None:
    """
    Преобразует str|datetime|None -> naive UTC datetime (для колонок TIMESTAMP в PG).
    """
    dt = _parse_iso(v)
    if not dt:
        return None
    # Для TIMESTAMP (без таймзоны) в PG лучше передавать naive UTC
    return dt.astimezone(timezone.utc).replace(tzinfo=None)

def _parse_iso(dt_val):
    """
    Принимает str | datetime | None -> возвращает aware datetime в UTC или None.
    """
    if not dt_val:
        return None
    if isinstance(dt_val, datetime):
        return dt_val.astimezone(timezone.utc) if dt_val.tzinfo else dt_val.replace(tzinfo=timezone.utc)
    try:
        # поддержка 'Z' и без 'Z'
        return datetime.fromisoformat(str(dt_val).replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


# ---------- USERS ----------
async def _init_users_sqlite(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            level TEXT,
            limitations TEXT,          -- JSON (list[str])
            equipment TEXT,            -- JSON (list[str])
            duration_minutes TEXT,
            free_workout_used INTEGER DEFAULT 0,
            extra_groups TEXT          -- JSON (list[str])
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
            duration_minutes TEXT,
            free_workout_used BOOLEAN DEFAULT FALSE,
            extra_groups TEXT
        )
    """)

async def save_user(user_id, level, limitations, equipment, duration_minutes, extra_groups=None):
    lim_json = json.dumps(limitations or [])
    eq_json  = json.dumps(equipment or [])
    ex_json  = json.dumps(extra_groups or [])
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                INSERT INTO users (user_id, level, limitations, equipment, duration_minutes, extra_groups)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    level = excluded.level,
                    limitations = excluded.limitations,
                    equipment = excluded.equipment,
                    duration_minutes = excluded.duration_minutes,
                    extra_groups = excluded.extra_groups
            """, (user_id, level, lim_json, eq_json, duration_minutes, ex_json))
            await db.commit()
    else:
        conn = await asyncpg.connect(PG_DSN)
        await conn.execute("""
            INSERT INTO users (user_id, level, limitations, equipment, duration_minutes, extra_groups)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user_id) DO UPDATE SET
                level = EXCLUDED.level,
                limitations = EXCLUDED.limitations,
                equipment = EXCLUDED.equipment,
                duration_minutes = EXCLUDED.duration_minutes,
                extra_groups = EXCLUDED.extra_groups
        """, user_id, level, lim_json, eq_json, duration_minutes, ex_json)
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
            return (
                row["user_id"],
                row["level"],
                row["limitations"],
                row["equipment"],
                row["duration_minutes"],
                row["free_workout_used"],
                row["extra_groups"],
            )
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
            email TEXT,           
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
            email TEXT,           
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)

async def get_subscription_email(user_id: int) -> str | None:
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT email FROM subscriptions WHERE user_id = ?", (user_id,)) as cur:
                row = await cur.fetchone()
                return row[0] if row else None
    else:
        conn = await asyncpg.connect(PG_DSN)
        row = await conn.fetchrow("SELECT email FROM subscriptions WHERE user_id = $1", user_id)
        await conn.close()
        return row["email"] if row else None

async def set_subscription_email(user_id: int, email: str):
    await upsert_subscription(user_id, email=email)


async def upsert_subscription(user_id: int, **fields):
    """
    Апсерт подписки с защитой:
    - если уже ACTIVE и период не истёк, запрещаем понижать статус;
    - запрещаем укорачивать current_period_end.
    """
    now = _now_iso()

    def _sanitize(existing_row, incoming: dict):
        if not existing_row:
            return incoming

        try:
            # asyncpg.Record
            old_status = existing_row["status"]
            old_cpe    = existing_row["current_period_end"]
        except Exception:
            # sqlite tuple
            old_status = existing_row[1]
            old_cpe    = existing_row[3]

        old_cpe_dt = _parse_iso(old_cpe)
        now_dt = datetime.now(timezone.utc)

        new = dict(incoming)

        if old_status == "active" and old_cpe_dt and old_cpe_dt > now_dt:
            # Разрешаем отмену продления (cancelled), но не даём даунгрейдить в trial/past_due
            if new.get("status") and new["status"] not in ("active", "cancelled"):
                new.pop("status", None)
            # Не укорачиваем период
            if "current_period_end" in new:
                new_cpe_dt = _parse_iso(new["current_period_end"])
                if new_cpe_dt and new_cpe_dt <= old_cpe_dt:
                    new.pop("current_period_end", None)


        return new

    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            # читаем текущую строку полностью
            async with db.execute("SELECT * FROM subscriptions WHERE user_id = ?", (user_id,)) as cur:
                existing = await cur.fetchone()

            fields = _sanitize(existing, fields)

            if existing:
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
        row = await conn.fetchrow("SELECT * FROM subscriptions WHERE user_id = $1", user_id)
        fields = _sanitize(row, fields)

        # нормализуем типы дат для PG (TIMESTAMP): ожидается datetime, не строка
        for k in ("current_period_end", "next_charge_at"):
            if k in fields:
                fields[k] = _to_pg_timestamp(fields[k])


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
            row["amount"], row["currency"], row["email"], 
            row["created_at"], row["updated_at"]
            )
        return None


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
            raw TEXT,
            confirmation_url TEXT,
            applied_at TEXT NULL
        )
    """)
    await conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_payments_payment_id ON payments(payment_id)")
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
            raw TEXT,
            confirmation_url TEXT,
            applied_at TIMESTAMPTZ NULL
        )
    """)
    await conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_payments_payment_id ON payments(payment_id)")


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


async def mark_payment_applied(payment_id: str) -> bool:
    """
    Ставит applied_at=NOW(), но только если было NULL.
    Возвращает True, если мы ПЕРВЫМИ отметили платёж как применённый.
    """
    if USE_SQLITE:
        now = _now_iso()
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute(
                "UPDATE payments SET applied_at = ? WHERE payment_id = ? AND applied_at IS NULL",
                (now, payment_id)
            )
            await db.commit()
            return cur.rowcount > 0  # True -> можно продлевать
    else:
        conn = await asyncpg.connect(PG_DSN)
        try:
            row = await conn.fetchrow(
                "UPDATE payments SET applied_at = NOW() "
                "WHERE payment_id = $1 AND applied_at IS NULL "
                "RETURNING applied_at",
                payment_id
            )
            return bool(row)  # True -> мы первые отметили платёж как применённый
        finally:
            await conn.close()

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

async def upsert_payment_status(
    user_id: int, payment_id: str, amount: int, currency: str,
    status: str, raw_text: str = "{}", confirmation_url: str | None = None
):
    """
    Обновляет запись о платеже (по payment_id), а если её нет — вставляет новую.
    Также корректно сохраняет confirmation_url.
    """
    now_iso = datetime.utcnow().isoformat()
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("""
                UPDATE payments
                   SET status = ?, amount = ?, currency = ?, raw = ?, created_at = ?, confirmation_url = ?
                 WHERE payment_id = ?
            """, (status, amount, currency, raw_text, now_iso, confirmation_url, payment_id))
            await db.commit()
            if cur.rowcount == 0:
                await db.execute("""
                    INSERT INTO payments (user_id, payment_id, amount, currency, status, created_at, raw, confirmation_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, payment_id, amount, currency, status, now_iso, raw_text, confirmation_url))
                await db.commit()
    else:
        conn = await asyncpg.connect(PG_DSN)
        row = await conn.fetchrow("""
            UPDATE payments
               SET status = $1, amount = $2, currency = $3, raw = $4, confirmation_url = $5
             WHERE payment_id = $6
         RETURNING id
        """, status, amount, currency, raw_text, confirmation_url, payment_id)
        if not row:
            await conn.execute("""
                INSERT INTO payments (user_id, payment_id, amount, currency, status, created_at, raw, confirmation_url)
                VALUES ($1, $2, $3, $4, $5, NOW(), $6, $7)
            """, user_id, payment_id, amount, currency, status, raw_text, confirmation_url)
        await conn.close()


async def get_payment_confirmation_url(payment_id: str) -> str | None:
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT confirmation_url FROM payments WHERE payment_id = ?", (payment_id,)) as cur:
                row = await cur.fetchone()
                return row[0] if row else None
    else:
        conn = await asyncpg.connect(PG_DSN)
        row = await conn.fetchrow("SELECT confirmation_url FROM payments WHERE payment_id = $1", payment_id)
        await conn.close()
        return row["confirmation_url"] if row else None
    

async def get_user_id_by_payment_id(payment_id: str) -> int | None:
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT user_id FROM payments WHERE payment_id = ?", (payment_id,)) as cur:
                row = await cur.fetchone()
                return row[0] if row else None
    else:
        conn = await asyncpg.connect(PG_DSN)
        row = await conn.fetchrow("SELECT user_id FROM payments WHERE payment_id = $1", payment_id)
        await conn.close()
        return row["user_id"] if row else None



async def get_last_pending_payment_id(user_id: int) -> str | None:
    """
    Возвращает payment_id последнего незавершённого платежа пользователя.
    """
    pending_states = ("pending", "waiting_for_capture")
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f"""
                SELECT payment_id
                  FROM payments
                 WHERE user_id = ? AND status IN ({",".join("?"*len(pending_states))})
              ORDER BY created_at DESC
                 LIMIT 1
            """, (user_id, *pending_states)) as cur:
                row = await cur.fetchone()
                return row[0] if row else None
    else:
        conn = await asyncpg.connect(PG_DSN)
        row = await conn.fetchrow("""
            SELECT payment_id
              FROM payments
             WHERE user_id = $1 AND status = ANY($2::text[])
          ORDER BY created_at DESC
             LIMIT 1
        """, user_id, list(pending_states))
        await conn.close()
        return row["payment_id"] if row else None
    
async def list_due_subscriptions(now_dt: datetime):
    """
    Возвращает список user_id, кому пора списывать.
    now_dt — aware datetime (UTC).
    """
    if USE_SQLITE:
        # в SQLite даты хранятся как TEXT → сравниваем по ISO-строке
        now_iso = (now_dt.astimezone(timezone.utc)).isoformat()
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("""
                SELECT user_id
                  FROM subscriptions
                 WHERE status = 'active'
                   AND payment_method_id IS NOT NULL
                   AND next_charge_at IS NOT NULL
                   AND next_charge_at <= ?
            """, (now_iso,)) as cur:
                rows = await cur.fetchall()
                return [r[0] for r in rows]
    else:
        conn = await asyncpg.connect(PG_DSN)
        try:
            # для TIMESTAMP без таймзоны — передаём naive UTC
            pg_now = now_dt.astimezone(timezone.utc).replace(tzinfo=None)
            rows = await conn.fetch("""
                SELECT user_id
                  FROM subscriptions
                 WHERE status = 'active'
                   AND payment_method_id IS NOT NULL
                   AND next_charge_at IS NOT NULL
                   AND next_charge_at <= $1
            """, pg_now)
            return [r["user_id"] for r in rows]
        finally:
            await conn.close()

    
async def cancel_other_pendings(user_id: int, keep_payment_id: str) -> int:
    """
    Локально помечает ВСЕ другие платежи пользователя со статусом pending/waiting_for_capture
    как 'canceled', кроме указанного keep_payment_id. Возвращает число обновлённых строк.
    """
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute(
                """
                UPDATE payments
                   SET status = 'canceled'
                 WHERE user_id = ?
                   AND payment_id <> ?
                   AND status IN ('pending','waiting_for_capture')
                """,
                (user_id, keep_payment_id)
            )
            await db.commit()
            return cur.rowcount or 0
    else:
        conn = await asyncpg.connect(PG_DSN)  # <-- было DSN
        try:
            res = await conn.execute(
                """
                UPDATE payments
                   SET status = 'canceled'
                 WHERE user_id = $1
                   AND payment_id <> $2
                   AND status = ANY($3::text[])
                """,
                user_id, keep_payment_id, ['pending','waiting_for_capture']
            )
            return int(res.split()[-1])  # 'UPDATE <n>'
        finally:
            await conn.close()

# db.py — вставить, например, под _init_exercises_pg()

def _ensure_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    try:
        return json.loads(v) if isinstance(v, str) else []
    except Exception:
        return []

async def get_all_exercises() -> list[dict]:
    """
    name:str, muscle_group:str, reps_note:str, video_url:str,
    levels:list[str], equipment:list[str], equipment_dnf:list[list[str]], allowed_limitations:list[str]
    """
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("""
                SELECT name, levels, equipment, equipment_dnf, allowed_limitations,
                       muscle_group, reps_note, video_url
                  FROM exercises
            """) as cur:
                rows = await cur.fetchall()
        # sqlite: индексы (tuple)
        result = []
        for r in rows:
            result.append({
                "name":               r[0],
                "levels":             _ensure_list(r[1]),
                "equipment":          _ensure_list(r[2]),
                "equipment_dnf":      _ensure_list(r[3]),
                "allowed_limitations":_ensure_list(r[4]),
                "muscle_group":       r[5],
                "reps_note":          r[6] or "",
                "video_url":          r[7] or "",
            })
        return result
    else:
        conn = await asyncpg.connect(PG_DSN)
        rows = await conn.fetch("""
            SELECT name, levels, equipment, equipment_dnf, allowed_limitations,
                   muscle_group, reps_note, video_url
              FROM exercises
        """)
        await conn.close()
        # pg: Record с уже «нормальными» типами (TEXT[], JSONB, …)
        result = []
        for r in rows:
            result.append({
                "name":               r["name"],
                "levels":             list(r["levels"] or []),
                "equipment":          list(r["equipment"] or []),
                "equipment_dnf":      r["equipment_dnf"] or [],
                "allowed_limitations":list(r["allowed_limitations"] or []),
                "muscle_group":       r["muscle_group"],
                "reps_note":          r["reps_note"] or "",
                "video_url":          r["video_url"] or "",
            })
        return result


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
