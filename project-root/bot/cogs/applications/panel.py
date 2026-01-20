import discord
from discord.ext import commands
from discord.ui import View, Button
from .dm_flow import start_application
from utils.application_cooldown import check_cooldown, set_cooldown
import math

class ApplicationPanel(discord.ui.View):
    timeout = None

    @discord.ui.button(label="🛡 Staff Application", style=discord.ButtonStyle.primary)
    async def staff(self, interaction: discord.Interaction, _):
        session = ApplicationSession(interaction.user.id, "staff")
        SESSIONS[interaction.user.id] = session
        await interaction.response.send_message(
            "📩 Check your DMs to continue the application.",
            ephemeral=True
        )
        await send_next_question(interaction.client, interaction.user, session)

    @discord.ui.button(label="💬 Chat Mod Application", style=discord.ButtonStyle.secondary)
    async def chatmod(self, interaction: discord.Interaction, _):
        await start_application(interaction, "chatmod")

    @discord.ui.button(label="🤝 Partner Manager", style=discord.ButtonStyle.success)
    async def partner(self, interaction: discord.Interaction, _):
        await start_application(interaction, "partner_manager")

class ApplicationPanelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="applicationpanel")
    @commands.has_permissions(administrator=True)
    async def panel(self, ctx):
        embed = discord.Embed(
            title="📋 Applications",
            description="Select the application you want to apply for.",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=ApplicationPanel())

async def setup(bot):
    await bot.add_cog(ApplicationPanelCog(bot))
