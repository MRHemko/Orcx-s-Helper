from main import cooldowns
from config.roles import APPLICATION_ROLES

@discord.ui.button(label="🛡 Staff Application", style=discord.ButtonStyle.primary)
async def staff(self, interaction: discord.Interaction, button: discord.ui.Button):

    ON_COOLDOWN, remaining = cooldowns.is_on_cooldown(
        interaction.user.id,
        "staff_application",
        cooldown_seconds=1209600  # 14d
    )

    if ON_COOLDOWN:
        await interaction.response.send_message(
            f"⏳ You can apply again in **{remaining // 3600}h {remaining % 3600 // 60}m**",
            ephemeral=True
        )
        return

    cooldowns.set_cooldown(interaction.user.id, "staff_application")

    await interaction.response.send_message(
        "📩 Check your DMs to continue the application.",
        ephemeral=True
    )

    await start_staff_application(interaction.user)

class ApplicationManageView(discord.ui.View):
    def __init__(self, applicant_id: int, application_type: str):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id
        self.application_type = application_type

    def disable_all_buttons(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

@discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success)
async def accept(self, interaction: discord.Interaction, _):

    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Staff only.", ephemeral=True)
        return

    guild = interaction.guild
    member = guild.get_member(self.applicant_id)

    role_id = APPLICATION_ROLES.get(self.application_type)
    role = guild.get_role(role_id)

    if member and role:
        await member.add_roles(role, reason="Application accepted")

        try:
            await member.send(
                f"✅ Your **{self.application_type.replace('_',' ').title()}** application was accepted."
            )
        except discord.Forbidden:
            pass

    self.disable_all_buttons()

    await interaction.message.edit(view=self)

    await interaction.channel.send(
        f"🎉 {member.mention} accepted."
    )

    await interaction.response.defer()

@discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.danger)
async def reject(self, interaction: discord.Interaction, _):

    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Staff only.", ephemeral=True)
        return

    await interaction.response.send_modal(
        RejectReasonModal(self.applicant_id, self.application_type)
    )

class RejectReasonModal(discord.ui.Modal, title="Reject Application"):
    reason = discord.ui.TextInput(
        label="Reason",
        style=discord.TextStyle.paragraph,
        required=True
    )

    def __init__(self, applicant_id: int, application_type: str):
        super().__init__()
        self.applicant_id = applicant_id
        self.application_type = application_type

        async def on_submit(self, interaction: discord.Interaction):
            member = interaction.guild.get_member(self.applicant_id)

            if member:
                try:
                    await member.send(
                        f"❌ Your **{self.application_type.replace('_', ' ').title()}** application was rejected.\n\n"
                        f"**Reason:**\n{self.reason.value}"
                    )
                except discord.Forbidden:
                    pass

            view = interaction.message.view
            if view:
                view.disable_all_buttons()
                await interaction.message.edit(view=view)

            await interaction.channel.send(
                f"❌ Application rejected.\n**Reason:** {self.reason.value}"
            )

            await interaction.response.defer()
