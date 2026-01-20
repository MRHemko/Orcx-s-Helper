import discord
from discord.ext import commands
from discord import app_commands

from bot.views.tickets import TicketView
from bot.services.ticket_service import create_ticket_channel


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ticket",
        description="Create a support ticket"
    )
    async def ticket(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Support Ticket",
            description="Staff will assist you shortly.",
            color=discord.Color.blurple()
        )

        channel = await create_ticket_channel(
            interaction,
            "support",
            embed
        )

        await channel.send(
            view=TicketView(interaction.user.id)
        )

        await interaction.response.send_message(
            f"✅ Ticket created: {channel.mention}",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))
