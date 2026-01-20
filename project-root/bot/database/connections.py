import aiosqlite


DB_PATH = "bot.db"


async def get_db():
return await aiosqlite.connect(DB_PATH)