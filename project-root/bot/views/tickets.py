import discord
from bot.services.ticket_service import close_ticket
from bot.config.settings import STAFF_ROLE_ID


class TicketView(discord.ui.View):
    timeout = None

    def __init__(self, owner_id: int):
        super().__init__()
        self.owner_id = owner_id
        self.claimed_by = None

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green)
    async def claim(self, interaction: discord.Interaction, _):
        if not any(r.id == STAFF_ROLE_ID for r in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Staff only.",
                ephemeral=True
            )
            return

        self.claimed_by = interaction.user.id
        await interaction.channel.send(
            f"📌 Claimed by {interaction.user.mention}"
        )
        await interaction.response.defer()

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, _):
        if not any(r.id == STAFF_ROLE_ID for r in interaction.user.roles):
            await interaction.response.send_message(
                "❌ Staff only.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            CloseTicketModal(self.owner_id)
        )


class CloseTicketModal(discord.ui.Modal, title="Close Ticket"):
    reason = discord.ui.TextInput(
        label="Close reason",
        required=True
    )

    def __init__(self, owner_id: int):
        super().__init__()
        self.owner_id = owner_id

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await close_ticket(
            interaction.channel,
            interaction.user,
            self.reason.value,
            self.owner_id
        )
