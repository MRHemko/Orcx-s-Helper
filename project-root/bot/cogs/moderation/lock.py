import discord
from discord.ext import commands

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=False
        )
        await ctx.send("🔒 Channel locked.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=True
        )
        await ctx.send("🔓 Channel unlocked.")

async def setup(bot):
    await bot.add_cog(Lock(bot))

