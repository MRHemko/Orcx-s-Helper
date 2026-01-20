import discord
from discord import app_commands
from datetime import timedelta
from database import log_action
from core.logs import send_mod_log

def setup(bot):

    @bot.tree.command(name="mute", description="Mute a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(
        interaction: discord.Interaction,
        member: discord.Member,
        duration: int,
        reason: str
    ):
        until = discord.utils.utcnow() + timedelta(minutes=duration)
        await member.timeout(until, reason=reason)

        await log_action(member.id, interaction.user.id, "mute", reason)

        embed = discord.Embed(
            title="🔇 Member Muted",
            color=discord.Color.orange()
        )
        embed.add_field(name="User", value=member.mention)
        embed.add_field(name="Duration", value=f"{duration} minutes")
        embed.add_field(name="Reason", value=reason)
        embed.set_footer(text=f"By {interaction.user}")

        await send_mod_log(interaction.guild, embed)

        await interaction.response.send_message(
            f"✅ {member.mention} muted for {duration} minutes.",
            ephemeral=True
        )

    @bot.tree.command(name="ban", description="Ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):
        await member.ban(reason=reason)

        await log_action(member.id, interaction.user.id, "ban", reason)

        embed = discord.Embed(
            title="🔨 Member Banned",
            color=discord.Color.red()
        )
        embed.add_field(name="User", value=f"{member} ({member.id})")
        embed.add_field(name="Reason", value=reason)
        embed.set_footer(text=f"By {interaction.user}")

        await send_mod_log(interaction.guild, embed)

        await interaction.response.send_message(
            f"🔨 {member} banned.",
            ephemeral=True
        )
