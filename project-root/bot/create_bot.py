import discord
from discord.ext import commands

def create_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.reactions = True
    intents.guilds = True
    intents.members = True

    bot = commands.Bot(
        command_prefix="!",
        intents=intents
    )

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")

    return bot
