import discord
from discord.ext import commands

from config import GUILD_ID


@bot.tree.command(name='reaction_roles', description='Send a panel fo reactions roles', guild=GUILD_ID)
async def reaction_roles(interaction: discord.Interaction, roles: discord.Role):
    # check admin
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You don't have the permissions to run this command", ephemeral=True)
        return

    embed = discord.Embed(title = "Reaction Roles", description = (
        "React to this message with the following emojis!")