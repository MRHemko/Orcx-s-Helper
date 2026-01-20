import discord
from bot.services.giveaway_services import add_entry, get_entry_count


class GiveawayView(discord.ui.View):
    timeout = None

    def __init__(self, giveaway_id):
        super().__init__()
        self.giveaway_id = giveaway_id

    @discord.ui.button(label="🎉 Enter (0)", style=discord.ButtonStyle.green)
    async def enter(self, interaction: discord.Interaction, button):
        success = add_entry(self.giveaway_id, interaction.user.id)
        if not success:
            await interaction.response.send_message(
                "❌ You already entered.",
                ephemeral=True
            )
            return

        count = get_entry_count(self.giveaway_id)
        button.label = f"🎉 Enter ({count})"
        await interaction.response.edit_message(view=self)
