import os
import json
import asyncpg
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

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
    conn = await asyncpg.connect(PG_DSN)
    await conn.execute("""
        INSERT INTO users (user_id, free_workout_used)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO UPDATE SET
            free_workout_used = EXCLUDED.free_workout_used
    """, user_id, used)
    await conn.close()


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
            plan TEXT NOT NULL DEFAULT 'month',
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)

async def get_subscription_email(user_id: int) -> str | None:
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

    def _norm_plan(v):
        if not v:
            return None
        v = str(v).strip().lower()
        return v if v in ("month", "year") else None

    def _sanitize(existing_row, incoming: dict):
        if not existing_row:
            plan = _norm_plan(incoming.get("plan"))
            if plan is None and "plan" in incoming:
                incoming.pop("plan", None)
            return incoming

        old_status = existing_row["status"]
        old_cpe    = existing_row["current_period_end"]
        old_plan   = (existing_row.get("plan") if isinstance(existing_row, dict) else None) or "month"

        old_cpe_dt = _parse_iso(old_cpe)
        now_dt = datetime.now(timezone.utc)

        new = dict(incoming)

        if "plan" in new:
            np = _norm_plan(new["plan"])
            if np is None:
                new.pop("plan", None)
            else:
                new["plan"] = np

        if old_status == "active" and old_cpe_dt and old_cpe_dt > now_dt:
            # статус: не понижаем
            if new.get("status") and new["status"] not in ("active", "cancelled"):
                new.pop("status", None)
            # период: не укорачиваем
            if "current_period_end" in new:
                new_cpe_dt = _parse_iso(new["current_period_end"])
                if new_cpe_dt and new_cpe_dt <= old_cpe_dt:
                    new.pop("current_period_end", None)
            # plan: не меняем на лету
            if "plan" in new and new["plan"] != old_plan:
                new.pop("plan", None)

        return new

    conn = await asyncpg.connect(PG_DSN)
    row = await conn.fetchrow("SELECT * FROM subscriptions WHERE user_id = $1", user_id)
    fields = _sanitize(row, fields)

    # нормализуем TIMESTAMP-поля
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
    conn = await asyncpg.connect(PG_DSN)
    row = await conn.fetchrow("SELECT * FROM subscriptions WHERE user_id = $1", user_id)
    await conn.close()
    if row:
        return (
            row["user_id"], row["status"], row["payment_method_id"],
            row["current_period_end"], row["next_charge_at"],
            row["amount"], row["currency"], row["email"],
            row["created_at"], row["updated_at"],
            row["plan"],  
        )
    return None


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

# db.py
async def _init_exercises_pg(conn):
    # Таблица "exercises": массивы и jsonb с дефолтами — как ожидает генератор
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
          name                TEXT PRIMARY KEY,
          levels              TEXT[] NOT NULL DEFAULT '{}',
          equipment           TEXT[] NOT NULL DEFAULT '{}',
          equipment_dnf       JSONB  NOT NULL DEFAULT '[]'::jsonb,
          allowed_limitations TEXT[] NOT NULL DEFAULT '{}',
          muscle_group        TEXT NOT NULL,
          reps_note           TEXT,
          video_url           TEXT
        );
    """)

    # Индексы под фильтрацию генератора (выполняются безопасно повторно)
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_ex_levels     ON exercises USING GIN (levels);")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_ex_equipment  ON exercises USING GIN (equipment);")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_ex_limits     ON exercises USING GIN (allowed_limitations);")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_ex_eqdnf      ON exercises USING GIN (equipment_dnf);")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_ex_group      ON exercises (muscle_group);")


async def upsert_payment_status(
    user_id: int, payment_id: str, amount: int, currency: str,
    status: str, raw_text: str = "{}", confirmation_url: str | None = None
):
    """
    Обновляет запись о платеже (по payment_id), а если её нет — вставляет новую.
    Также корректно сохраняет confirmation_url.
    """
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
    conn = await asyncpg.connect(PG_DSN)
    row = await conn.fetchrow("SELECT confirmation_url FROM payments WHERE payment_id = $1", payment_id)
    await conn.close()
    return row["confirmation_url"] if row else None
    
async def get_user_id_by_payment_id(payment_id: str) -> int | None:
    conn = await asyncpg.connect(PG_DSN)
    row = await conn.fetchrow("SELECT user_id FROM payments WHERE payment_id = $1", payment_id)
    await conn.close()
    return row["user_id"] if row else None

async def get_last_pending_payment_id(user_id: int) -> str | None:
    """
    Возвращает payment_id последнего незавершённого платежа пользователя.
    """
    pending_states = ("pending", "waiting_for_capture")
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


def _ensure_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    try:
        return json.loads(v) if isinstance(v, str) else []
    except Exception:
        return []
    
def _ensure_eqdnf(v) -> list[list[str]]:
    """
    Возвращает list[list[str]] независимо от того, пришло ли это
    как JSON-строка, JSONB, список строк и т.п.
    """
    if v is None or v == "":
        return []

    # Верхний уровень может быть строкой с JSON
    if isinstance(v, str):
        s = v.strip()
        try:
            v = json.loads(s)
        except Exception:
            return [[s]] if s else []

    if not isinstance(v, list):
        return []

    out: list[list[str]] = []
    for opt in v:
        if isinstance(opt, list):
            cleaned = [str(x).strip() for x in opt if str(x).strip()]
            if cleaned:
                out.append(cleaned)
        elif isinstance(opt, str):
            s = opt.strip()
            if not s:
                continue
            # Вложенная JSON-строка?
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    cleaned = [str(x).strip() for x in parsed if str(x).strip()]
                    if cleaned:
                        out.append(cleaned)
                else:
                    out.append([s])
            except Exception:
                out.append([s])
        # остальные типы пропускаем
    return out


async def get_all_exercises() -> list[dict]:
    """
    name:str, muscle_group:str, reps_note:str, video_url:str,
    levels:list[str], equipment:list[str], equipment_dnf:list[list[str]], allowed_limitations:list[str]
    """
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
            "equipment_dnf":      _ensure_eqdnf(r["equipment_dnf"] or []),
            "allowed_limitations":list(r["allowed_limitations"] or []),
            "muscle_group":       r["muscle_group"],
            "reps_note":          r["reps_note"] or "",
            "video_url":          r["video_url"] or "",
        })
    return result


# -------- init all --------
async def init_db():
    conn = await asyncpg.connect(PG_DSN)
    await _init_users_pg(conn)
    await _init_subscriptions_pg(conn)
    await _init_payments_pg(conn)
    await _init_exercises_pg(conn)
    await conn.close()