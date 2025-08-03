import aiosqlite
import json

DB_PATH = "user_data.db"

async def init_db():
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

async def save_user(user_id, level, limitations, equipment, duration_minutes):
    limitations_json = json.dumps(limitations)
    equipment_json = json.dumps(equipment)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR REPLACE INTO users (user_id, level, limitations, equipment, duration_minutes)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, level, limitations_json, equipment_json, duration_minutes))
        await db.commit()
