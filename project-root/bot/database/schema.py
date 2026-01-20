from database.connection import get_db


async def init_db():
db = await get_db()
await db.execute("""
CREATE TABLE IF NOT EXISTS giveaway_entries (user_id INTEGER PRIMARY KEY)
""")
await db.execute("""
CREATE TABLE IF NOT EXISTS scam_vouches (
target_id INTEGER,
from_id INTEGER
)
""")
VOUCHES_TABLE = """
CREATE TABLE IF NOT EXISTS vouches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id INTEGER NOT NULL,
    from_id INTEGER NOT NULL,
    type TEXT NOT NULL, -- 'vouch' | 'scam'
    message TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
"""
GIVEAWAYS_TABLE = """
CREATE TABLE IF NOT EXISTS giveaways (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER,
    channel_id INTEGER,
    guild_id INTEGER,
    host_id INTEGER,
    prize TEXT,
    winners INTEGER,
    ends_at INTEGER,
    ended INTEGER DEFAULT 0
);
"""
ENTRIES_TABLE = """
CREATE TABLE IF NOT EXISTS giveaway_entries (
    giveaway_id INTEGER,
    user_id INTEGER,
    UNIQUE(giveaway_id, user_id)
);
"""

CREATE_APPLICATION_COOLDOWN_TABLE = """
CREATE TABLE IF NOT EXISTS application_cooldowns (
    user_id INTEGER PRIMARY KEY,
    last_applied TIMESTAMP
)
"""

await db.commit()
await db.close()