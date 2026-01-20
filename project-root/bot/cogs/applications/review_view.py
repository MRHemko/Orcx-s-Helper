import discord
from datetime import datetime
from bot.config import APPLICATION_ROLES, STAFF_ROLE_ID
from bot.config import (
    APPLICATION_ACCEPTED_CHANNEL_ID,
    APPLICATION_REJECTED_CHANNEL_ID
)

class ApplicationReviewView(discord.ui.View):
    timeout = None

    def __init__(self, applicant_id: int, app_type: str):
        super().__init__()
        self.applicant_id = applicant_id
        self.app_type = app_type
        self.resolved = False

    def disable_all(self):
        for item in self.children:
            item.disabled = True

    # ✅ ACCEPT
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not any(r.id == STAFF_ROLE_ID for r in interaction.user.roles):
            await interaction.response.send_message("❌ Staff only.", ephemeral=True)
            return

        if self.resolved:
            await interaction.response.send_message("❌ Already handled.", ephemeral=True)
            return

        self.resolved = True
        self.disable_all()

        guild = interaction.guild
        member = guild.get_member(self.applicant_id)

        role_id = APPLICATION_ROLES.get(self.app_type)
        role = guild.get_role(role_id) if role_id else None

        if member and role:
            await member.add_roles(role, reason="Application accepted")

        # ✉ DM user
        if member:
            try:
                await member.send(
                    f"✅ **Your {self.app_type.replace('_',' ').title()} application was ACCEPTED!**\n"
                    f"Welcome to the team."
                )
            except discord.Forbidden:
                pass

        # 📝 Update embed
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.add_field(
            name="Status",
            value=f"✅ Accepted by {interaction.user.mention}",
            inline=False
        )
        embed.timestamp = datetime.utcnow()

        await interaction.message.delete()

        await interaction.message.edit(embed=embed, view=self)

        archive_channel = interaction.guild.get_channel(
            APPLICATION_ACCEPTED_CHANNEL_ID
        )

        if archive_channel:
            await archive_channel.send(
                embed=embed
            )

        await interaction.message.delete()

        await interaction.response.defer()

    # ❌ REJECT
    @discord.ui.button(label="Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not any(r.id == STAFF_ROLE_ID for r in interaction.user.roles):
            await interaction.response.send_message("❌ Staff only.", ephemeral=True)
            return

        if self.resolved:
            await interaction.response.send_message("❌ Already handled.", ephemeral=True)
            return

        await interaction.response.send_modal(
            RejectReasonModal(self)
        )

class RejectReasonModal(discord.ui.Modal, title="Reject Application"):
    reason = discord.ui.TextInput(
        label="Reason for rejection",
        style=discord.TextStyle.paragraph,
        required=True
    )

    def __init__(self, view: ApplicationReviewView):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        self.view.resolved = True
        self.view.disable_all()

        guild = interaction.guild
        member = guild.get_member(self.view.applicant_id)

        archive_channel = interaction.guild.get_channel(
            APPLICATION_REJECTED_CHANNEL_ID
        )

        if archive_channel:
            await archive_channel.send(
                embed=embed
            )

        await interaction.message.delete()

        # DM käyttäjälle
        if member:
            try:
                await member.send(
                    f"❌ **Your {self.view.app_type.replace('_',' ').title()} application was rejected.**\n\n"
                    f"**Reason:** {self.reason.value}"
                )
            except discord.Forbidden:
                pass

        # Update embed
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.add_field(
            name="Status",
            value=(
                f"❌ Rejected by {interaction.user.mention}\n"
                f"**Reason:** {self.reason.value}"
            ),
            inline=False
        )
        embed.timestamp = datetime.utcnow()

        await interaction.message.edit(embed=embed, view=self.view)
        await interaction.response.defer()
