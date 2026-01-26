import discord
from discord.ext import commands
import os

INITIAL_EXTENSIONS = [
    "cogs.tickets",
    "cogs.giveaways",
    "cogs.moderation",
]

def create_bot():
    intents = discord.Intents.all()

    bot = commands.Bot(
        command_prefix="!",
        intents=intents
    )

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")

        for ext in INITIAL_EXTENSIONS:
            try:
                await bot.load_extension(ext)
                print(f"Loaded {ext}")
            except Exception as e:
                print(f"Failed to load {ext}: {e}")

    return bot
