import os
import json
import aiosqlite
import asyncpg
from dotenv import load_dotenv

load_dotenv()

USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"

DB_PATH = "user_data.db"
PG_DSN = os.getenv("DATABASE_URL") 

async def init_db():
    if USE_SQLITE: #local development
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    level TEXT,
                    limitations TEXT,
                    equipment TEXT,
                    duration_minutes INTEGER
                )
            ''')
            await db.commit()
    else:
        conn = await asyncpg.connect(PG_DSN)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                level TEXT,
                limitations TEXT,
                equipment TEXT,
                duration_minutes INTEGER
            )
        ''')
        await conn.close()

async def save_user(user_id, level, limitations, equipment, duration_minutes):
    limitations_json = json.dumps(limitations)
    equipment_json = json.dumps(equipment)
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                INSERT OR REPLACE INTO users (user_id, level, limitations, equipment, duration_minutes)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, level, limitations_json, equipment_json, duration_minutes))
            await db.commit()
    else:
        conn = await asyncpg.connect(PG_DSN)
        await conn.execute('''
            INSERT INTO users (user_id, level, limitations, equipment, duration_minutes)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id)
            DO UPDATE SET level = EXCLUDED.level,
                          limitations = EXCLUDED.limitations,
                          equipment = EXCLUDED.equipment,
                          duration_minutes = EXCLUDED.duration_minutes
        ''', user_id, level, limitations_json, equipment_json, duration_minutes)
        await conn.close()

async def get_user(user_id):
    if USE_SQLITE:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
                return await cursor.fetchone()
    else:
        conn = await asyncpg.connect(PG_DSN)
        row = await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)
        await conn.close()
        if row:
            return (
                row['user_id'],
                row['level'],
                row['limitations'],
                row['equipment'],
                row['duration_minutes']
            )
        return None
