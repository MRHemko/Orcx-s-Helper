import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
from datetime import datetime

from bot.services.scam_service import check_and_assign_scammer

DB_PATH = "bot.db"


class Vouches(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="scam",
        description="Report a user as a scammer"
    )
    async def scam(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str
    ):
        if user.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ You cannot scam-report yourself.",
                ephemeral=True
            )
            return

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO vouches (target_id, from_id, type, message, timestamp)
                VALUES (?, ?, 'scam', ?, ?)
                """,
                (
                    user.id,
                    interaction.user.id,
                    reason,
                    datetime.utcnow().isoformat()
                )
            )
            await db.commit()

        await check_and_assign_scammer(user)

        embed = discord.Embed(
            title="⚠️ Scam Report Submitted",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="Reported by", value=interaction.user.mention)
        embed.add_field(name="Reason", value=reason)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Vouches(bot))