import aiosqlite

DB = "bot.db"

async def init_moderation():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS mutes (
            user_id INTEGER,
            guild_id INTEGER,
            unmute_at INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS mod_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            target_id INTEGER,
            staff_id INTEGER,
            reason TEXT,
            timestamp INTEGER
        )
        """)
        await db.commit()
