import os
from dotenv import load_dotenv

from bot.core.create_bot import create_bot
from bot.database.database import init_db

# 1️⃣ Lataa ympäristömuuttujat ENSIN
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing from environment variables")

# 2️⃣ Luo bot YHDESSÄ paikassa
bot = create_bot()


# 3️⃣ Lataa cogit
async def load_cogs():
    await bot.load_extension("bot.cogs.applications.panel")
    await bot.load_extension("bot.cogs.tickets.panel")
    await bot.load_extension("bot.cogs.giveaway")
    await bot.load_extension("bot.cogs.moderation.lock")


# 4️⃣ setup_hook = oikea paikka async-initille
@bot.event
async def setup_hook():
    await init_db()
    await load_cogs()


# 5️⃣ on_ready vain loggausta varten
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


# 6️⃣ AJA BOTTI TASAN KERRAN
def main():
    bot.run(TOKEN)


if __name__ == "__main__":
    main()