ALLOWED_GIVEAWAY_CHANNEL_IDS = [
    1378407284090077204,  # giveaway
    1400833986934210634,  # daily giveaway
    1441413547082121379   # quick drops
]

class GiveawayClaimView(discord.ui.View):
    timeout = 300

    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.guild = guild
        self.channel: discord.TextChannel | None = None
        self.host: discord.Member | None = None

        # Täytä channel-select
        self.select_channel.options = [
            discord.SelectOption(label=ch.name, value=str(ch.id))
            for ch in guild.text_channels
            if "giveaway" in ch.name.lower()
        ]

        # Täytä staff-host select
        self.select_host.options = [
            discord.SelectOption(label=m.display_name, value=str(m.id))
            for m in guild.members
            if any(r.id == STAFF_ROLE_ID for r in m.roles)
        ]

    @discord.ui.select(
        placeholder="Select giveaway channel",
        min_values=1,
        max_values=1
    )
    async def select_channel(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.channel = interaction.guild.get_channel(int(select.values[0]))
        await interaction.response.defer(ephemeral=True)

    @discord.ui.select(
        placeholder="Select giveaway host (staff)",
        min_values=1,
        max_values=1
    )
    async def select_host(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.host = interaction.guild.get_member(int(select.values[0]))
        await interaction.response.defer(ephemeral=True)

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.success)
    async def continue_button(self, interaction: discord.Interaction, _):
        if not self.channel or not self.host:
            await interaction.response.send_message(
                "❌ Please select both channel and host.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            GiveawayClaimModal(self.channel, self.host)
        )

class GiveawayClaimModal(discord.ui.Modal, title="Giveaway Claim"):
    ign = discord.ui.TextInput(label="Your IGN", required=True)
    amount = discord.ui.TextInput(label="Prize amount", required=True)

    def __init__(self, channel: discord.TextChannel, host: discord.Member):
        super().__init__()
        self.channel = channel
        self.host = host

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title="🎁 Giveaway Claim",
            color=discord.Color.orange()
        )
        embed.add_field(name="IGN", value=self.ign.value, inline=False)
        embed.add_field(name="Prize", value=self.amount.value, inline=False)
        embed.add_field(name="Giveaway Channel", value=self.channel.mention)
        embed.add_field(name="Host", value=self.host.mention)

        try:
            await create_ticket(interaction, "giveaway_claim", embed)
        except Exception as e:
            await interaction.followup.send(
                f"❌ Ticket creation failed:\n```{e}```",
                ephemeral=True
            )