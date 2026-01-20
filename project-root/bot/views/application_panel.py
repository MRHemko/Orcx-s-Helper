import discord
from bot.config.applications import APPLICATIONS
from datetime import datetime, timedelta

BUTTON_COOLDOWN = {}

if interaction.user.id in BUTTON_COOLDOWN:
    if datetime.utcnow() - BUTTON_COOLDOWN[interaction.user.id] < timedelta(minutes=5):
        await interaction.response.send_message(
            "⏳ Please wait before applying again.",
            ephemeral=True
        )
        return

BUTTON_COOLDOWN[interaction.user.id] = datetime.utcnow()

class ApplicationPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Make a selection",
        options=[
            discord.SelectOption(label=v["label"], value=k)
            for k, v in APPLICATIONS.items()
        ]
    )
    async def select(self, interaction: discord.Interaction, select):
        interaction.client.selected_application = select.values[0]
        await interaction.response.send_message(
            "📩 Check your DMs to continue the application.",
            ephemeral=True
        )
