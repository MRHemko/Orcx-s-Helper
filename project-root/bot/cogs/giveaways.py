import time
import discord
from discord.ext import commands, tasks
from discord import app_commands

from bot.views.giveaway import GiveawayView
from bot.services.giveaway_services import (
    create_giveaway,
    pick_winners,
    mark_ended
)
from bot.database.connections import db
from bot.config.settings import STAFF_ROLE_ID


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    @app_commands.command(name="giveaway")
    async def giveaway(
        self,
        interaction: discord.Interaction,
        prize: str,
        duration_minutes: int,
        winners: int
    ):
        if not any(r.id == STAFF_ROLE_ID for r in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Staff only.",
                ephemeral=True
            )
            return

        giveaway_id = create_giveaway(
            interaction.channel.id,
            interaction.guild.id,
            interaction.user.id,
            prize,
            winners,
            duration_minutes * 60
        )

        embed = discord.Embed(
            title="🎉 Giveaway",
            description=f"**Prize:** {prize}\n"
                        f"**Winners:** {winners}\n"
                        f"Ends <t:{int(time.time()) + duration_minutes*60}:R>",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"ID: {giveaway_id}")

        msg = await interaction.channel.send(
            embed=embed,
            view=GiveawayView(giveaway_id)
        )

        db.execute(
            "UPDATE giveaways SET message_id = ? WHERE id = ?",
            (msg.id, giveaway_id)
        )
        db.commit()

        await interaction.response.send_message(
            "✅ Giveaway started.",
            ephemeral=True
        )

    @app_commands.command(name="reroll")
    async def reroll(self, interaction: discord.Interaction, giveaway_id: int):
        if not any(r.id == STAFF_ROLE_ID for r in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Staff only.",
                ephemeral=True
            )
            return

        winners = pick_winners(giveaway_id, 1)
        mentions = ", ".join(f"<@{u}>" for u in winners) or "No entries"

        await interaction.channel.send(
            f"🔁 **Rerolled Winner:** {mentions}"
        )
        await interaction.response.send_message(
            "✅ Rerolled.",
            ephemeral=True
        )

    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        now = int(time.time())
        cur = db.execute(
            "SELECT * FROM giveaways WHERE ended = 0 AND ends_at <= ?",
            (now,)
        )

        for g in cur.fetchall():
            channel = self.bot.get_channel(g["channel_id"])
            if not channel:
                continue

            winners = pick_winners(g["id"], g["winners"])
            mentions = ", ".join(f"<@{u}>" for u in winners) or "No entries"

            await channel.send(
                f"🎉 **Giveaway Ended!**\n"
                f"Prize: **{g['prize']}**\n"
                f"Winners: {mentions}"
            )

            mark_ended(g["id"])


async def setup(bot):
    await bot.add_cog(Giveaways(bot))
