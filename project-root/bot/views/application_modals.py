import discord


class StaffApplicationModal(discord.ui.Modal, title="Staff Application"):
    age = discord.ui.TextInput(label="Age", required=True)
    experience = discord.ui.TextInput(label="Staff experience", style=discord.TextStyle.paragraph)
    activity = discord.ui.TextInput(label="Daily activity (hours)")
    why = discord.ui.TextInput(label="Why should we choose you?", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.client.create_application_ticket(
            interaction, "staff", self
        )


class ChatModApplicationModal(discord.ui.Modal, title="Chat Moderator Application"):
    age = discord.ui.TextInput(label="Age", required=True)
    languages = discord.ui.TextInput(label="Languages you speak")
    timezone = discord.ui.TextInput(label="Timezone")
    activity = discord.ui.TextInput(label="Daily activity")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.client.create_application_ticket(
            interaction, "chatmod", self
        )


class PartnerManagerApplicationModal(discord.ui.Modal, title="Partner Manager Application"):
    age = discord.ui.TextInput(label="Age")
    experience = discord.ui.TextInput(label="Partner experience", style=discord.TextStyle.paragraph)
    contacts = discord.ui.TextInput(label="How will you find partners?")
    why = discord.ui.TextInput(label="Why this role?", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.client.create_application_ticket(
            interaction, "partner", self
        )
