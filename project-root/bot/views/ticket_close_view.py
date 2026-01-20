import discord

class CloseReasonModal(discord.ui.Modal, title="Close Ticket"):
    reason = discord.ui.TextInput(
        label="Reason for closing",
        required=True,
        style=discord.TextStyle.paragraph
    )

    def __init__(self, ticket_view):
        super().__init__()
        self.ticket_view = ticket_view

    async def on_submit(self, interaction: discord.Interaction):
        await self.ticket_view.final_close(interaction, self.reason.value)


class ReopenView(discord.ui.View):
    timeout = None

    @discord.ui.button(label="🔁 Reopen Ticket", style=discord.ButtonStyle.green)
    async def reopen(self, interaction: discord.Interaction, _):
        await interaction.channel.edit(archived=False)
        await interaction.channel.send("🔓 Ticket reopened.")
        await interaction.response.defer()
