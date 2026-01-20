import random
import aiosqlite
from datetime import datetime
from database import DB_NAME

async def get_entries():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT user_id FROM giveaway_entries")
        return [u[0] for u in await cur.fetchall()]

async def add_entry(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO giveaway_entries VALUES (?)",
            (user_id,)
        )
        await db.commit()

async def entry_count():
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT COUNT(*) FROM giveaway_entries")
        (count,) = await cur.fetchone()
        return count

def pick_winners(users, amount):
    return random.sample(users, min(len(users), amount))
