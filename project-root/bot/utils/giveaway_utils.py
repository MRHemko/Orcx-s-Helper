import discord
from datetime import datetime

from bot.config.giveaway import (
    DAILY_PRIZE,
    DAILY_WINNERS,
    GIVEAWAY_HOST_ID,
    GIVEAWAY_HOST_NAME,
)

def build_giveaway_embed(end_time: int, entries: int) -> discord.Embed:
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
