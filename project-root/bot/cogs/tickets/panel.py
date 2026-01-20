from .modals import *
from .giveaway_claim import GiveawayClaimView
from .embeds import ticket_panel_embed

class TicketPanelView(discord.ui.View):
    timeout = None

    @discord.ui.button(label="📩 Support", style=discord.ButtonStyle.primary)
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SupportModal())

    @discord.ui.button(label="🤝 Partner", style=discord.ButtonStyle.primary)
    async def partner(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PartnerModal())

    @discord.ui.button(label="🛒 Market", style=discord.ButtonStyle.secondary)
    async def market(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MarketModal())

    @discord.ui.button(label="🎁 Giveaway Claim", style=discord.ButtonStyle.success)
    async def giveaway_claim(self, interaction: discord.Interaction, _):
        await interaction.response.send_message(
            "Please select giveaway details:",
            view=GiveawayClaimView(interaction.guild),
            ephemeral=True
        )

    @discord.ui.button(label="🎥 Media", style=discord.ButtonStyle.secondary)
    async def media(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MediaModal())

    @discord.ui.button(label="💰 Sponsor Giveaway", style=discord.ButtonStyle.success)
    async def sponsor(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SponsorModal())

class TicketPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketpanel", description="Send the ticket panel")
    async def ticketpanel(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=embed,
            view=TicketPanelView()
        )

async def setup(bot):
    await bot.add_cog(TicketPanel(bot))

@bot.command(name="ticketpanel")
@commands.has_permissions(administrator=True)
async def ticketpanel_prefix(ctx):
    embed = discord.Embed(
        title="🎫 Orcx's Ocean — Ticket Center",
        description=(
            "**Please choose the ticket type that best fits your request.**\n\n"

            "### 👷 Support\n"
            "> Need help with refunds, issues, or general questions?\n"
            "> Click **📩 Support** to contact our support team.\n\n"

            "### 🤝 Partnership\n"
            "> Interested in partnering with Orcx's Ocean?\n"
            "> Click **🤝 Partner** to submit a partnership request.\n\n"

            "### 🛒 Market\n"
            "> Want to sell spawners or make a market-related request?\n"
            "> Click **🛒 Market** to proceed.\n\n"

            "### 🎉 Giveaway Claim\n"
            "> Won a giveaway and need to claim your prize?\n"
            "> Click **🎁 Giveaway Claim** to continue.\n\n"

            "### 🎥 Media / VIP\n"
            "> Applying for Media or VIP?\n"
            "> Click **🎥 Media** to apply.\n\n"

            "### 💰 Sponsor Giveaway\n"
            "> Want to sponsor a giveaway for the community?\n"
            "> Click **💰 Sponsor Giveaway** to get started."
        ),
        color=discord.Color.blurple()
    )

    embed.set_footer(text="Orcx's Ocean • Support System")
    await ctx.send(embed=embed, view=TicketPanelView())