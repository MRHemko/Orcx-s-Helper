import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from database import init_db

load_dotenv()

from utils.cooldowns import CooldownManager

cooldowns = CooldownManager()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await init_db()
    print(f"✅ Logged in as {bot.user}")

async def load_cogs():
    await bot.load_extension("cogs.applications.panel")
    await bot.load_extension("cogs.tickets.panel")
    await bot.load_extension("cogs.giveaway.daily")
    await bot.load_extension("cogs.moderation.lock")

@bot.event
async def setup_hook():
    await load_cogs()

bot.run(os.getenv("DISCORD_TOKEN"))
