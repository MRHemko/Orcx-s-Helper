import discord

class AnswerSelect(discord.ui.View):
    def __init__(self, options):
        super().__init__(timeout=300)
        self.value = None

        self.select = discord.ui.Select(
            placeholder="Choose one",
            options=[
                discord.SelectOption(label=o, value=o)
                for o in options
            ]
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        self.value = self.select.values[0]
        await interaction.response.defer()
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        self.value = interaction.data["values"][0]
        await interaction.response.defer()
        self.stop()
        return True

from bot.config.applications import APPLICATIONS

async def run_application(bot, user, app_key):
    app = APPLICATIONS[app_key]
    questions = app["questions"]
    answers = []

    dm = await user.create_dm()

    for index, q in enumerate(questions, start=1):
        if q["type"] == "text":
            await dm.send(f"**{index}. {q['question']}**")
            msg = await bot.wait_for(
                "message",
                check=lambda m: m.author == user and m.channel == dm
            )
            answers.append(msg.content)

        elif q["type"] == "select":
            view = AnswerSelect(q["options"])
            await dm.send(f"**{index}. {q['question']}**", view=view)
            await view.wait()
            answers.append(view.value)

    return answers

