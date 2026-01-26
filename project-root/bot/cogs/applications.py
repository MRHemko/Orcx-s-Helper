import discord
from discord.ext import commands
from bot.services.applications.cooldown import can_apply, is_blacklisted, save_apply
from bot.services.applications.flow import start_application
from bot.config.applications import APPLICATIONS
from bot.views.applications.review import ApplicationReviewView

APPLICATION_LOG_CHANNEL_ID = 1444614714637156486


class Applications(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.type == discord.InteractionType.component:
            return

        if not hasattr(self.bot, "selected_application"):
            return

        user = interaction.user
        key = self.bot.selected_application

        if is_blacklisted(user.id):
            await interaction.response.send_message(
                "❌ You are blacklisted from applications.",
                ephemeral=True
            )
            return

        if not can_apply(user.id):
            await interaction.response.send_message(
                "⏳ You are on cooldown.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        answers = await start_application(self.bot, user, key)
        save_apply(user.id)

        embed = discord.Embed(
            title=f"{APPLICATIONS[key]['label']} Application",
            color=discord.Color.green()
        )

        for q, a in answers.items():
            embed.add_field(name=q, value=a, inline=False)

        log = interaction.guild.get_channel(APPLICATION_LOG_CHANNEL_ID)

        await log.send(
            content=user.mention,
            embed=embed,
            view=ApplicationReviewView(
                user.id,
                APPLICATIONS[key]["role_id"]
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Applications(bot))
