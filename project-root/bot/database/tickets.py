import aiosqlite
from datetime import datetime

DB = "bot.db"

async def init_ticket_stats():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS ticket_stats (
            channel_id INTEGER PRIMARY KEY,
            owner_id INTEGER,
            ticket_type TEXT,
            claimed_by INTEGER,
            opened_at TEXT,
            closed_at TEXT
        )
        """)
        await db.commit()
