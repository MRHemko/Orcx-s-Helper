import discord
from bot.config.settings import APPLICATION_LOG_CHANNEL_ID
from datetime import datetime


class CloseReasonModal(discord.ui.Modal, title="Close Application"):
    reason = discord.ui.TextInput(
        label="Close reason",
        style=discord.TextStyle.paragraph,
        required=True
    )

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        log_channel = interaction.guild.get_channel(APPLICATION_LOG_CHANNEL_ID)

        if log_channel:
            embed = discord.Embed(
                title="📄 Application Closed",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Channel", value=self.channel.name)
            embed.add_field(name="Closed by", value=interaction.user.mention)
            embed.add_field(name="Reason", value=self.reason.value)

            await log_channel.send(embed=embed)

        await self.channel.delete()


class ApplicationTicketView(discord.ui.View):
    timeout = None

    def __init__(self, owner_id: int):
        super().__init__()
        self.owner_id = owner_id

    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, _):
        await interaction.response.send_modal(
            CloseReasonModal(interaction.channel)
        )