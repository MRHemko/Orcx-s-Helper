import aiosqlite
import asyncio
import pytest

@pytest.mark.asyncio
async def test_sqlite_connection():
    async with aiosqlite.connect(":memory:") as db:
        await db.execute("CREATE TABLE test (id INTEGER)")
        await db.commit()
