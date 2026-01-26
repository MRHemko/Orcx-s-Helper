import discord
from discord.ext import commands
from .manage import TicketManageView

class TicketEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        if not message.channel.name.startswith(tuple(TICKET_TYPES.keys())):
            return

        for view in self.bot.persistent_views:
            if isinstance(view, TicketManageView) and view.owner_id:
                if view.owner_id != message.author.id:
                    await view.auto_claim(message.author, message.channel)

class TicketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lock")
    async def lock(self, ctx):
        if not any(r.id == STAFF_ROLE_ID for r in ctx.author.roles):
            return

        channel = ctx.channel
        if not channel.category or channel.category.id != TICKET_CATEGORY_ID:
            return

        owner_id = int(channel.name.split("-")[-1])
        owner = ctx.guild.get_member(owner_id)

        if owner:
            await channel.set_permissions(
                owner,
                send_messages=False,
                view_channel=True
            )

        await ctx.send("🔒 Ticket locked.")

    @commands.command(name="unlock")
    async def unlock(self, ctx):
        if not any(r.id == STAFF_ROLE_ID for r in ctx.author.roles):
            return

        channel = ctx.channel
        if not channel.category or channel.category.id != TICKET_CATEGORY_ID:
            return

        owner_id = int(channel.name.split("-")[-1])
        owner = ctx.guild.get_member(owner_id)

        if owner:
            await channel.set_permissions(
                owner,
                send_messages=True,
                view_channel=True
            )

        await ctx.send("🔓 Ticket unlocked.")
