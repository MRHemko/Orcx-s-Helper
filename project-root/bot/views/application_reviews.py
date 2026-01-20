import discord

class ApplicationReviewView(discord.ui.View):
    def __init__(self, user_id, role_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.role_id = role_id

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, _):
        member = interaction.guild.get_member(self.user_id)
        role = interaction.guild.get_role(self.role_id)

        if member and role:
            await member.add_roles(role)
            await member.send(
                f"✅ You have been **accepted** for {role.name}!"
            )

        await interaction.message.edit(content="✅ Accepted", view=None)

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, _):
        await interaction.response.send_modal(
            RejectReasonModal(interaction.message)
        )


class RejectReasonModal(discord.ui.Modal, title="Reject reason"):
    reason = discord.ui.TextInput(
        label="Reason for rejection",
        style=discord.TextStyle.paragraph,
        required=True
    )

    def __init__(self, message: discord.Message):
        super().__init__()
        self.message = message

    async def on_submit(self, interaction: discord.Interaction):
        embed = self.message.embeds[0]
        embed.color = discord.Color.red()
        embed.add_field(name="❌ Rejected", value=self.reason.value, inline=False)

        await self.message.edit(embed=embed, view=None)
        await interaction.response.send_message("Application rejected.", ephemeral=True)
