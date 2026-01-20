import aiosqlite
import discord
from datetime import datetime
from bot.config.settings import (
    SCAMMER_ROLE_ID,
    SCAM_LOG_CHANNEL_ID,
    SCAM_LIMIT
)

DB_PATH = "bot.db"


async def get_unique_scam_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT COUNT(DISTINCT from_id)
            FROM vouches
            WHERE target_id = ?
              AND type = 'scam'
            """,
            (user_id,)
        )
        (count,) = await cursor.fetchone()
        return count


async def check_and_assign_scammer(member: discord.Member):
    scam_count = await get_unique_scam_count(member.id)

    if scam_count < SCAM_LIMIT:
        return False

    role = member.guild.get_role(SCAMMER_ROLE_ID)
    if not role or role in member.roles:
        return False

    await member.add_roles(
        role,
        reason=f"Reached {SCAM_LIMIT} unique scam vouches"
    )

    # 📢 Log
    log_channel = member.guild.get_channel(SCAM_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="🚨 Scammer Role Assigned",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(
            name="User",
            value=f"{member.mention} (`{member.id}`)",
            inline=False
        )
        embed.add_field(
            name="Scam vouches",
            value=f"{scam_count}/{SCAM_LIMIT}",
            inline=True
        )

        await log_channel.send(embed=embed)

    # 📩 DM
    try:
        await member.send(
            f"🚨 You have been given the **Scammer** role.\n"
            f"Reason: {scam_count} unique scam reports."
        )
    except discord.Forbidden:
        pass

    return True
