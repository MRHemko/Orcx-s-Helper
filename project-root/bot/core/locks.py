import discord
from discord.ext import commands

def setup(bot):

    @bot.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(ctx):
        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=False
        )
        await ctx.send("🔒 Channel locked.")

    @bot.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(ctx):
        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=True
        )
        await ctx.send("🔓 Channel unlocked.")
