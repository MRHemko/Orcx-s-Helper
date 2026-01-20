import discord

class AnswerSelect(discord.ui.View):
    def __init__(self, options):
        super().__init__(timeout=300)
        self.value = None

        self.select = discord.ui.Select(
            options=[discord.SelectOption(label=o, value=o) for o in options]
        )
        self.select.callback = self.callback
        self.add_item(self.select)

    async def callback(self, interaction: discord.Interaction):
        self.value = self.select.values[0]
        await interaction.response.defer()
        self.stop()
