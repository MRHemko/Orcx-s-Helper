import time
import aiosqlite

COOLDOWN_SECONDS = 7 * 24 * 60 * 60  # 7 days
DB_PATH = "bot.db"

async def check_cooldown(user_id: int, app_type: str) -> int | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT last_applied FROM application_cooldowns WHERE user_id=? AND application_type=?",
            (user_id, app_type)
        )
        row = await cursor.fetchone()

        if not row:
            return None

        elapsed = time.time() - row[0]
        if elapsed >= COOLDOWN_SECONDS:
            return None

        return int(COOLDOWN_SECONDS - elapsed)


async def set_cooldown(user_id: int, app_type: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO application_cooldowns (user_id, application_type, last_applied)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, application_type)
            DO UPDATE SET last_applied=excluded.last_applied
            """,
            (user_id, app_type, int(time.time()))
        )
        await db.commit()
