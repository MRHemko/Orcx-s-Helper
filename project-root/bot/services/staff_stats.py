import aiosqlite

DB = "database/tickets.db"

async def init_staff_stats():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS staff_stats (
            staff_id INTEGER PRIMARY KEY,
            handled INTEGER DEFAULT 0,
            total_seconds INTEGER DEFAULT 0
        )
        """)
        await db.commit()


async def log_ticket_close(staff_id: int, duration_seconds: int):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        INSERT INTO staff_stats (staff_id, handled, total_seconds)
        VALUES (?, 1, ?)
        ON CONFLICT(staff_id)
        DO UPDATE SET
            handled = handled + 1,
            total_seconds = total_seconds + excluded.total_seconds
        """, (staff_id, duration_seconds))
        await db.commit()


async def get_staff_stats(staff_id: int):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT handled, total_seconds FROM staff_stats WHERE staff_id = ?",
            (staff_id,)
        )
        return await cur.fetchone()
