import aiosqlite

DB_NAME = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            user_id INTEGER,
            type TEXT,
            answers TEXT,
            created_at TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS application_cooldowns (
            user_id INTEGER PRIMARY KEY,
            last_used TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS daily_giveaway_entries (
            user_id INTEGER PRIMARY KEY
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS vouches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_id INTEGER,
            from_id INTEGER,
            type TEXT,
            message TEXT,
            timestamp TEXT
        )
        """)



        async def init_giveaway_db():
            async with aiosqlite.connect(DB_NAME) as db:
                await db.execute("""
                                 CREATE TABLE IF NOT EXISTS giveaways
                                 (
                                     message_id
                                     INTEGER,
                                     channel_id
                                     INTEGER,
                                     end_time
                                     INTEGER
                                 )
                                 """)

                await db.execute("""
                                 CREATE TABLE IF NOT EXISTS giveaway_entries
                                 (
                                     user_id
                                     INTEGER
                                     PRIMARY
                                     KEY
                                 )
                                 """)

        await db.commit()
