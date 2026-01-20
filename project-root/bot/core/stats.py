import discord
from discord import app_commands
import aiosqlite

DB_PATH = "bot.db"

def setup(bot):

    @bot.tree.command(name="stats", description="Show moderation stats")
    async def stats(interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user

        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM mod_logs WHERE user_id = ?",
                (user.id,)
            )
            (count,) = await cursor.fetchone()

        embed = discord.Embed(
            title="📊 Moderation Stats",
            color=discord.Color.blurple()
        )
        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="Actions", value=count)

        await interaction.response.send_message(embed=embed)
