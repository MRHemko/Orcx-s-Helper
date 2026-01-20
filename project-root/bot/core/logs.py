import discord
from config import MOD_LOG_CHANNEL_ID

async def send_mod_log(guild, embed):
    channel = guild.get_channel(MOD_LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)
