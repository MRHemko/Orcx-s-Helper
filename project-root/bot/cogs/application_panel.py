import discord
from discord.ext import commands
from discord import app_commands
from bot.views.application_panel import ApplicationPanelView


class ApplicationPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="applications", description="Send application panel")
    async def applications(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📋 Applications",
            description=(
                "Choose the application you want to submit:\n\n"
                "👮 Staff\n"
                "💬 Chat Moderator\n"
                "🤝 Partner Manager"
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(
            embed=embed,
            view=ApplicationPanelView()
        )


async def setup(bot):
    await bot.add_cog(ApplicationPanel(bot))
