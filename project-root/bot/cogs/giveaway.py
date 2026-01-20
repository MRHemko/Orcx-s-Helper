# cogs/giveaway.py
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from config import *
from views.giveaway_view import DailyGiveawayView
from services.giveaway_service import get_entries, pick_winners

_current_end_time = None

def get_end_time():
    return _current_end_time

def build_giveaway_embed(end_time, entries):
    embed = discord.Embed(
        title="🎉 DAILY GIVEAWAY",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="🎁 Prize", value=DAILY_PRIZE, inline=True)
    embed.add_field(name="🏆 Winners", value=str(DAILY_WINNERS), inline=True)
    embed.add_field(name="🎟 Entries", value=str(entries), inline=True)
    embed.add_field(name="⏰ Ends", value=f"<t:{end_time}:R>", inline=False)
    embed.add_field(
        name="👤 Hosted by",
        value=f"<@{GIVEAWAY_HOST_ID}> | {GIVEAWAY_HOST_NAME}",
        inline=False
    )
    return embed

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily.start()

    @tasks.loop(hours=24)
    async def daily(self):
        global _current_end_time
        channel = self.bot.get_channel(DAILY_GIVEAWAY_CHANNEL_ID)
        role = channel.guild.get_role(GIVEAWAY_PING_ROLE_ID)

        _current_end_time = int(
            (datetime.utcnow() + timedelta(seconds=DAILY_DURATION)).timestamp()
        )

        embed = build_giveaway_embed(_current_end_time, 0)

        await channel.send(
            content=f"{role.mention}\n{GIVEAWAY_CUSTOM_MESSAGE}",
            embed=embed,
            view=DailyGiveawayView()
        )

        await discord.utils.sleep_until(
            datetime.fromtimestamp(_current_end_time)
        )

        users = await get_entries()
        winners = pick_winners(users, DAILY_WINNERS)
        mentions = " ".join(f"<@{u}>" for u in winners)

        await channel.send(f"🏆 Winner(s): {mentions}")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
