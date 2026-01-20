import discord
from bot.views.application_dm import AnswerSelect
from bot.config.applications import APPLICATIONS

async def run_application(bot, user, key):
    app = APPLICATIONS[key]
    answers = []
    dm = await user.create_dm()

    for i, q in enumerate(app["questions"], start=1):
        if q["type"] == "text":
            await dm.send(f"**{i}. {q['q']}**")
            msg = await bot.wait_for(
                "message",
                check=lambda m: m.author == user and m.channel == dm
            )
            answers.append(msg.content)

        else:
            view = AnswerSelect(q["options"])
            await dm.send(f"**{i}. {q['q']}**", view=view)
            await view.wait()
            answers.append(view.value)

    return answers
