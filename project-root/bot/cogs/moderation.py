# cogs/moderation.py
import discord
from discord.ext import commands
from discord import app_commands
from bot.config import *
from bot.services.moderation_service import lock_channel, unlock_channel

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ========= LOCK =========
    @app_commands.command(name="lock", description="Lock the channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        await lock_channel(interaction.channel)
        await interaction.response.send_message(
            f"{LOCK_EMOJI} Channel locked."
        )

    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock_prefix(self, ctx):
        await lock_channel(ctx.channel)
        await ctx.send(f"{LOCK_EMOJI} Channel locked.")

    # ========= UNLOCK =========
    @app_commands.command(name="unlock", description="Unlock the channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        await unlock_channel(interaction.channel)
        await interaction.response.send_message(
            f"{UNLOCK_EMOJI} Channel unlocked."
        )

    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock_prefix(self, ctx):
        await unlock_channel(ctx.channel)
        await ctx.send(f"{UNLOCK_EMOJI} Channel unlocked.")

    # ========= MUTE =========
    @app_commands.command(name="mute", description="Mute a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        role = interaction.guild.get_role(MUTE_ROLE_ID)
        await member.add_roles(role, reason=reason)

        await interaction.response.send_message(
            f"🔇 {member.mention} muted.\nReason: {reason}"
        )

    # ========= BAN =========
    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        await member.ban(reason=reason)
        await interaction.response.send_message(
            f"🔨 {member} banned.\nReason: {reason}"
        )

    # ========= STATS =========
    @commands.command(name="stats")
    async def stats(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        embed = discord.Embed(
            title="📊 User Stats",
            color=discord.Color.blurple()
        )
        embed.add_field(name="User", value=member.mention)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(
            name="Account Created",
            value=f"<t:{int(member.created_at.timestamp())}:R>"
        )
        embed.add_field(
            name="Joined Server",
            value=f"<t:{int(member.joined_at.timestamp())}:R>"
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
