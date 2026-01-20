import aiosqlite
import time

DB_PATH = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        with open("database/schema.sql") as f:
            await db.executescript(f.read())
        await db.commit()

async def init_moderation_tables():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS mod_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            staff_id INTEGER,
            action TEXT,
            reason TEXT,
            timestamp TEXT
        )
        """)
        await db.commit()

async def log_action(user_id, staff_id, action, reason):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO mod_logs VALUES (NULL, ?, ?, ?, ?, ?)",
            (user_id, staff_id, action, reason, datetime.utcnow().isoformat())
        )
        await db.commit

async def init_ticket_tables():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            channel_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            claimed_by INTEGER,
            status TEXT,
            created_at TEXT
        )
        """)
        await db.commit()

await db.execute("""
CREATE TABLE IF NOT EXISTS ticket_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    staff_id INTEGER,
    action TEXT NOT NULL, -- open / close
    created_at TEXT NOT NULL
)
""")
await db.commit()

await db.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    channel_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    priority TEXT NOT NULL DEFAULT 'MEDIUM',
    created_at TEXT NOT NULL
)
""")
await db.commit()
