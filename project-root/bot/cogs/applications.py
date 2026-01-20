import discord
from discord.ext import commands
from bot.views.application_panel import ApplicationPanel
from bot.services.application_flow import run_application
from bot.services.application_cooldown import can_apply, save_apply
from bot.views.application_review import ApplicationReviewView
from bot.config.applications import APPLICATIONS
from bot.services.application_cooldown import is_blacklisted
from config import APPLICATIONS
from utils.application_sessions import SESSIONS, ApplicationSession
from views.application_views import ChoiceView

APPLICATION_LOG_CHANNEL_ID = 1444614714637156486

if is_blacklisted(user.id):
    await interaction.response.send_message(
        "❌ You are blacklisted from applications.",
        ephemeral=True
    )
    return

async def send_next_question(bot, user, session):
    app = APPLICATIONS[session.app_key]
    questions = app["questions"]

    if session.index >= len(questions):
        await finish_application(bot, user, session)
        return

    q = questions[session.index]

    if q["type"] == "text":
        await user.send(q["question"])

        def check(m):
            return m.author.id == user.id and isinstance(m.channel, discord.DMChannel)

        msg = await bot.wait_for("message", check=check)
        session.answers[q["id"]] = msg.content
        session.index += 1
        await send_next_question(bot, user, session)

    elif q["type"] == "choice":
        view = ChoiceView(session, q)
        view.select.options = [
            discord.SelectOption(label=o) for o in q["options"]
        ]
        await user.send(q["question"], view=view)


async def finish_application(bot, user, session):
    app = APPLICATIONS[session.app_key]
    embed = discord.Embed(
        title=app["title"],
        color=discord.Color.blurple()
    )

    for q in app["questions"]:
        embed.add_field(
            name=q["question"],
            value=session.answers.get(q["id"], "N/A"),
            inline=False
        )

    guild = bot.guilds[0]
    log = guild.get_channel(app["log_channel_id"])
    await log.send(content=user.mention, embed=embed)

    await user.send("✅ Your application has been submitted!")
    SESSIONS.pop(user.id)

class Applications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not hasattr(self.bot, "selected_application"):
            return

        key = self.bot.selected_application
        user = interaction.user

        if not can_apply(user.id):
            return

        answers = await run_application(self.bot, user, key)
        save_apply(user.id)

        embed = discord.Embed(
            title=f"{APPLICATIONS[key]['label']} Submitted",
            color=discord.Color.green()
        )

        from bot.database.connections import db

        db.execute(
            "INSERT INTO application_stats VALUES (?, ?, CURRENT_TIMESTAMP)",
            (user.id, key)
        )

        for i, ans in enumerate(answers, start=1):
            embed.add_field(name=f"Q{i}", value=ans, inline=False)

        log = interaction.guild.get_channel(APPLICATION_LOG_CHANNEL_ID)

        await log.send(
            embed=embed,
            view=ApplicationReviewView(
                user.id,
                APPLICATIONS[key]["role_id"]
            )
        )

async def setup(bot):
    await bot.add_cog(Applications(bot))
