import discord

class MultipleChoiceView(discord.ui.View):
    def __init__(self, question: str, options: list[str]):
        super().__init__(timeout=300)
        self.question = question
        self.answer = None

        self.select.options = [
            discord.SelectOption(
                label=opt,
                value=opt
            ) for opt in options
        ]

    @discord.ui.select(
        placeholder="Select one option",
        min_values=1,
        max_values=1
    )
    async def select(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):
        self.answer = select.values[0]
        await interaction.response.send_message(
            f"✅ Selected: **{self.answer}**",
            ephemeral=True
        )
        self.stop()
