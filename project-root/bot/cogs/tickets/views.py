class TicketPriorityView(discord.ui.View):
    timeout = 60

    @discord.ui.select(
        placeholder="Select ticket priority",
        options=[
            discord.SelectOption(label="Low", value="LOW", emoji="🟢"),
            discord.SelectOption(label="Medium", value="MEDIUM", emoji="🟡"),
            discord.SelectOption(label="High", value="HIGH", emoji="🔴")
        ]
    )
    async def select_priority(self, interaction: discord.Interaction, select: discord.ui.Select):
        from .ticket_create import create_ticket
        await create_ticket(interaction, select.values[0])
