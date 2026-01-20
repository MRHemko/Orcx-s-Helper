import discord

async def lock_channel(channel: discord.TextChannel):
    overwrite = channel.overwrites_for(channel.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(channel.guild.default_role, overwrite=overwrite)

async def unlock_channel(channel: discord.TextChannel):
    overwrite = channel.overwrites_for(channel.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(channel.guild.default_role, overwrite=overwrite)
