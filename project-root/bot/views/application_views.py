import discord
from services.application_service import run_application
from config.applications import APPLICATIONS

class ChoiceView(discord.ui.View):
    def __init__(self, session, question):
        super().__init__(timeout=300)
        self.session = session
        self.question = question

    @discord.ui.select(placeholder="Choose one option", min_values=1, max_values=1)
    async def select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.session.answers[self.question["id"]] = select.values[0]
        self.session.index += 1
        await interaction.response.defer()
        await send_next_question(interaction.client, interaction.user, self.session)

class ApplicationSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=data["label"],
                value=key
            )
            for key, data in APPLICATIONS.items()
        ]

        super().__init__(
            placeholder="Make a selection",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "📩 Check your DMs to continue the application.",
            ephemeral=True
        )

        answers = await run_application(
            interaction.client,
            interaction.user,
            self.values[0]
        )

        await send_application_embed(
            interaction,
            self.values[0],
            answers
        )


class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ApplicationSelect())

async def send_application_embed(interaction, app_key, answers):
    log_channel = interaction.guild.get_channel(APPLICATION_LOG_CHANNEL_ID)

    embed = discord.Embed(
        title=f"{interaction.user.name}'s {APPLICATIONS[app_key]['label']} Application Submitted",
        color=discord.Color.green()
    )

    for i, (q, a) in enumerate(zip(APPLICATIONS[app_key]["questions"], answers), start=1):
        embed.add_field(
            name=f"{i}. {q}",
            value=a,
            inline=False
        )

    embed.add_field(
        name="Submission stats",
        value=(
            f"UserId: {interaction.user.id}\n"
            f"Username: {interaction.user.name}\n"
            f"User: {interaction.user.mention}\n"
            f"Joined guild: {interaction.user.joined_at.strftime('%Y-%m-%d')}"
        ),
        inline=False
    )

    await log_channel.send(embed=embed)
