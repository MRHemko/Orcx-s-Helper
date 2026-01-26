import discord
from discord.ext import commands
from discord import app_commands
from bot.services.staff_stats import get_staff_stats
from bot.services.sla_service import format_duration

class TicketStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketstats", description="View staff ticket stats")
    async def stats(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user

        data = await get_staff_stats(member.id)
        if not data:
            await interaction.response.send_message(
                "No ticket data found.", ephemeral=True
            )
            return

        handled, total_seconds = data
        avg = total_seconds // handled if handled else 0

        embed = discord.Embed(
            title="📊 Ticket Stats",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Staff", value=member.mention)
        embed.add_field(name="Handled", value=str(handled))
        embed.add_field(name="Avg SLA", value=format_duration(avg))

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(TicketStats(bot))
