import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

from bot.views.giveaway_view import DailyGiveawayView
from bot.utils.giveaway_utils import build_giveaway_embed
from bot.services.giveaway_services import get_entries, pick_winners
from bot.config.giveaway import (
    DAILY_GIVEAWAY_CHANNEL_ID,
    GIVEAWAY_PING_ROLE_ID,
    DAILY_WINNERS,
    DAILY_DURATION,
    GIVEAWAY_CUSTOM_MESSAGE,
)

_current_end_time = None

def get_end_time():
    return _current_end_time


class Giveaway(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.daily.start()

    @tasks.loop(hours=24)
    async def daily(self):
        global _current_end_time

        channel = self.bot.get_channel(DAILY_GIVEAWAY_CHANNEL_ID)
        if channel is None:
            return  # estää crashin jos cache ei ole valmis

        role = channel.guild.get_role(GIVEAWAY_PING_ROLE_ID)

        _current_end_time = int(
            (datetime.utcnow() + timedelta(seconds=DAILY_DURATION)).timestamp()
        )

        embed = build_giveaway_embed(_current_end_time, 0)

        await channel.send(
            content=f"{role.mention if role else ''}\n{GIVEAWAY_CUSTOM_MESSAGE}",
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

    @daily.before_loop
    async def before_daily(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Giveaway(bot))

