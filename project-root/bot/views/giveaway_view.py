import discord
from services.giveaway_service import add_entry, entry_count
from cogs.giveaway import build_giveaway_embed, get_end_time

class DailyGiveawayView(discord.ui.View):
    timeout = None

    @discord.ui.button(label="🎉 Join Giveaway", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            await add_entry(interaction.user.id)
        except:
            return await interaction.response.send_message(
                "❌ You already joined.",
                ephemeral=True
            )

        count = await entry_count()
        embed = build_giveaway_embed(get_end_time(), count)

        await interaction.message.edit(embed=embed)
        await interaction.response.send_message(
            "✅ You joined the giveaway!",
            ephemeral=True
        )
