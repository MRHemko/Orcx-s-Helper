class SupportModal(discord.ui.Modal, title="Support Ticket"):
    reason = discord.ui.TextInput(label="Why do you need support?", required=True)
    ign = discord.ui.TextInput(label="IGN (if refund)", required=False)
    amount = discord.ui.TextInput(label="Amount owed (if refund)", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(title="🛠 Support Ticket", color=discord.Color.blurple())
        embed.add_field(name="Reason", value=self.reason.value, inline=False)
        embed.add_field(name="IGN", value=self.ign.value or "N/A")
        embed.add_field(name="Amount", value=self.amount.value or "N/A")

        try:
            await create_ticket(interaction, "support", embed)
        except Exception as e:
            await interaction.followup.send(
                f"❌ Ticket creation failed:\n```{e}```",
                ephemeral=True
            )

class PartnerModal(discord.ui.Modal, title="Partner Application"):
    members = discord.ui.TextInput(label="How many members does your server have?")
    read = discord.ui.TextInput(label="Have you read partner requirements?")
    donut = discord.ui.TextInput(label="Is your server DonutSMP related?")
    rules = discord.ui.TextInput(label="Does your server follow DonutSMP rules?")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(title="🤝 Partner Application", color=discord.Color.green())
        embed.add_field(name="Members", value=self.members.value)
        embed.add_field(name="Read Requirements", value=self.read.value)
        embed.add_field(name="DonutSMP Related", value=self.donut.value)
        embed.add_field(name="Follows Rules", value=self.rules.value)

        try:
            await create_ticket(interaction, "partner", embed)
        except Exception as e:
            await interaction.followup.send(
                f"❌ Ticket creation failed:\n```{e}```",
                ephemeral=True
            )


class MarketModal(discord.ui.Modal, title="Market Ticket"):
    buy_sell = discord.ui.TextInput(label="Buying or selling?")
    prices = discord.ui.TextInput(label="Have you read spawner prices?")
    amount = discord.ui.TextInput(label="How many?")
    spawner = discord.ui.TextInput(label="Spawner type?")
    agree = discord.ui.TextInput(label="Agree scamming = ban?")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(title="🛒 Market Ticket", color=discord.Color.gold())
        embed.add_field(name="Type", value=self.buy_sell.value)
        embed.add_field(name="Prices Read", value=self.prices.value)
        embed.add_field(name="Amount", value=self.amount.value)
        embed.add_field(name="Spawner", value=self.spawner.value)
        embed.add_field(name="Agreement", value=self.agree.value)

        try:
            await create_ticket(interaction, "market", embed)
        except Exception as e:
            await interaction.followup.send(
                f"❌ Ticket creation failed:\n```{e}```",
                ephemeral=True
            )


class SponsorModal(discord.ui.Modal, title="Sponsor Giveaway"):
    amount = discord.ui.TextInput(label="How much do you sponsor?")
    ign = discord.ui.TextInput(label="Your IGN")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(title="💰 Sponsor Giveaway", color=discord.Color.purple())
        embed.add_field(name="Amount", value=self.amount.value)
        embed.add_field(name="IGN", value=self.ign.value)

        try:
            await create_ticket(interaction, "sponsor_giveaway", embed)
        except Exception as e:
            await interaction.followup.send(
                f"❌ Ticket creation failed:\n```{e}```",
                ephemeral=True
            )



class MediaModal(discord.ui.Modal, title="Media Ticket"):
    ign = discord.ui.TextInput(label="Your IGN")
    proof = discord.ui.TextInput(label="Proof of MC ownership", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(title="🎥 Media Ticket", color=discord.Color.teal())
        embed.add_field(name="IGN", value=self.ign.value)
        embed.add_field(name="Proof", value=self.proof.value)

        try:
            await create_ticket(interaction, "media", embed)
        except Exception as e:
            await interaction.followup.send(
                f"❌ Ticket creation failed:\n```{e}```",
                ephemeral=True
            )

class CloseReasonModal(discord.ui.Modal, title="Close Ticket"):
    reason = discord.ui.TextInput(
        label="Reason for closing this ticket",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )

    def __init__(self, manage_view):
        super().__init__()
        self.manage_view = manage_view

    async def on_submit(self, interaction: discord.Interaction):
        await self.manage_view.final_close(interaction, self.reason.value)

from .create_ticket import create_ticket