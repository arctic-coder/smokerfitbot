# scripts/seed_exercises_from_json.py
import os, json, asyncio
from pathlib import Path

# Тянем конфиг/инициализацию из проекта
os.environ.setdefault("USE_SQLITE", os.getenv("USE_SQLITE", "true"))
from db import USE_SQLITE, DB_PATH, PG_DSN, init_db  # noqa

async def _seed_sqlite(rows):
    import aiosqlite, json as _json
    async with aiosqlite.connect(DB_PATH) as db:
        for r in rows:
            await db.execute("""
                INSERT INTO exercises
                  (name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                  levels = excluded.levels,
                  equipment = excluded.equipment,
                  equipment_dnf = excluded.equipment_dnf,
                  allowed_limitations = excluded.allowed_limitations,
                  muscle_group = excluded.muscle_group,
                  reps_note = excluded.reps_note,
                  video_url = excluded.video_url
            """, (
                r["name"],
                _json.dumps(r["levels"], ensure_ascii=False),
                _json.dumps(r["equipment"], ensure_ascii=False),
                _json.dumps(r["equipment_dnf"], ensure_ascii=False),
                _json.dumps(r["allowed_limitations"], ensure_ascii=False),
                r["muscle_group"], r["reps_note"], r["video_url"]
            ))
        await db.commit()
    print(f"SQLite: upserted {len(rows)} rows")

async def _seed_pg(rows):
    import asyncpg, json as _json
    conn = await asyncpg.connect(PG_DSN)
    try:
        for r in rows:
            await conn.execute("""
                INSERT INTO exercises
                  (name, levels, equipment, equipment_dnf, allowed_limitations, muscle_group, reps_note, video_url)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT(name) DO UPDATE SET
                  levels = EXCLUDED.levels,
                  equipment = EXCLUDED.equipment,
                  equipment_dnf = EXCLUDED.equipment_dnf,
                  allowed_limitations = EXCLUDED.allowed_limitations,
                  muscle_group = EXCLUDED.muscle_group,
                  reps_note = EXCLUDED.reps_note,
                  video_url = EXCLUDED.video_url
            """, (
                r["name"],
                r["levels"],                              # TEXT[]
                r["equipment"],                           # TEXT[]
                _json.dumps(r["equipment_dnf"], ensure_ascii=False),  # JSONB
                r["allowed_limitations"],                 # TEXT[]
                r["muscle_group"], r["reps_note"], r["video_url"]
            ))
    finally:
        await conn.close()
    print(f"Postgres: upserted {len(rows)} rows")

async def main(json_path: str = "data/exercises.json"):
    await init_db()  # создаст таблицы при необходимости
    data = json.loads(Path(json_path).read_text("utf-8"))
    if not isinstance(data, list):
        raise SystemExit("Invalid JSON: expected list")
    if USE_SQLITE:
        await _seed_sqlite(data)
    else:
        await _seed_pg(data)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--file", default="data/exercises.json")
    args = p.parse_args()
    asyncio.run(main(args.file))
