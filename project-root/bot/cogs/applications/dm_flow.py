import discord
import json
from datetime import datetime, timedelta
import aiosqlite

from bot.config import (
    APPLICATION_COOLDOWN_HOURS,
    APPLICATION_REVIEW_CHANNEL_ID,
    APPLICATION_ROLES
)
from bot.database import DB_NAME
from .questions import APPLICATION_QUESTIONS
from .question_views import MultipleChoiceView

async def ask_multiple_choice(
    user: discord.User,
    question: str,
    options: list[str]
) -> str:
    embed = discord.Embed(
        title="📋 Application Question",
        description=(
            f"**{question}**\n\n" +
            "\n".join(
                f"{i+1}. {opt}" for i, opt in enumerate(options)
            )
        ),
        color=discord.Color.blurple()
    )

    view = MultipleChoiceView(question, options)

    await user.send(embed=embed, view=view)
    await view.wait()

    return view.answer


TIMEOUT_SECONDS = 300  # 5 min / kysymys


async def start_application(interaction: discord.Interaction, app_type: str):
    user = interaction.user

    # 🔒 Cooldown check
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT last_used FROM application_cooldowns WHERE user_id = ?",
            (user.id,)
        )
        row = await cursor.fetchone()

        if row:
            last_used = datetime.fromisoformat(row[0])
            if datetime.utcnow() - last_used < timedelta(hours=APPLICATION_COOLDOWN_HOURS):
                await interaction.response.send_message(
                    "❌ You can only apply once every 24 hours.",
                    ephemeral=True
                )
                return

    # 📩 Avaa DM
    try:
        dm = await user.create_dm()
        await dm.send(
            f"📋 **{app_type.replace('_', ' ').title()} Application**\n"
            "Please answer the following questions.\n"
            "You have **5 minutes per question**.\n\n"
            "Type `cancel` to stop."
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I can't DM you. Please enable DMs.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        "📩 I've sent you the application questions in DM.",
        ephemeral=True
    )

    answers = []
    questions = APPLICATION_QUESTIONS[app_type]

    def check(m: discord.Message):
        return m.author.id == user.id and m.channel == dm

    for index, question in enumerate(questions, start=1):
        await dm.send(f"**{index}. {question}**")

        try:
            msg = await interaction.client.wait_for(
                "message",
                timeout=TIMEOUT_SECONDS,
                check=check
            )
        except TimeoutError:
            await dm.send("⏰ Application timed out.")
            return

        if msg.content.lower() == "cancel":
            await dm.send("❌ Application cancelled.")
            return

        answers.append(msg.content)

    # 💾 Tallenna tietokantaan
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO application_cooldowns VALUES (?, ?)",
            (user.id, datetime.utcnow().isoformat())
        )

        await db.execute(
            "INSERT INTO applications VALUES (?, ?, ?, ?)",
            (
                user.id,
                app_type,
                json.dumps(answers),
                datetime.utcnow().isoformat()
            )
        )
        await db.commit()

    # 📤 Lähetä review-kanavaan
    guild = interaction.guild
    review_channel = guild.get_channel(APPLICATION_REVIEW_CHANNEL_ID)

    from .review_view import ApplicationReviewView

    await review_channel.send(
        embed=embed,
        view=ApplicationReviewView(
            applicant_id=user.id,
            app_type=app_type
        )
    )

    embed.add_field(name="User", value=user.mention, inline=False)
    embed.add_field(name="User ID", value=str(user.id), inline=False)
    embed.add_field(
        name="Experience",
        value=answers["experience"],
        inline=False
    )

    for q, a in zip(questions, answers):
        embed.add_field(
            name=q,
            value=a[:1024],
            inline=False
        )

    embed.set_footer(text="Application System")

    if review_channel:
        await review_channel.send(embed=embed)

    # ✅ Ilmoitus käyttäjälle
    await dm.send(
        "✅ **Your application has been submitted successfully.**\n"
        "Please wait for staff to review it."
    )
