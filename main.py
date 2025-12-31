import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from datetime import datetime, timedelta, timezone
import os
import logging
from dotenv import load_dotenv
from flask import Flask
import threading
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path

WARN_FILE = Path("warnings.json")

MAX_WARNS_PER_MONTH = 5
MUTE_AT_WARN = 3
BAN_AT_WARN = 5
MUTE_DURATION = timedelta(days=7)

def load_warnings():
    if WARN_FILE.exists():
        with open(WARN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_warnings(data):
    with open(WARN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

WARNINGS = load_warnings()

WELCOME_CHANNEL_ID = 1378411602990338058

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_web).start()

GUILD_ID = 1378407104632586373
MY_GUILD = discord.Object(id=GUILD_ID)

# --- Load environment ---
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# --- Bot setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Duration parser ---
def parse_duration(duration: str) -> int:
    duration = duration.lower().strip()
    number = ""
    for char in duration:
        if char.isdigit():
            number += char
        else:
            unit = char
            break
    else:
        unit = "s"
    number = int(number)
    if unit == "s":
        return number
    elif unit == "m":
        return number * 60
    elif unit == "h":
        return number * 3600
    elif unit == "d":
        return number * 86400
    else:
        raise ValueError("Invalid duration! Use s, m, h, or d.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        synced = await bot.tree.sync(guild=MY_GUILD)
        print(f"Synced {len(synced)} guild commands")
    except Exception as e:
        print(e)

@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.get_channel(1378411602990338058)
    if channel is None:
        return

    embed = discord.Embed(
        title="New member Alert!",
        description=(
            f"**Welcome to Orcx's Ocean**\n\n"
            f"Welcome {member.mention}\n\n"
            f"Check Out 🎉 <#1378407284090077204> For Big Giveaway\n"
            f"Check Out 🎁 <#1400833986934210634> For Daily Giveaway\n"
            f"Check Out ⚡ <#1441413547082121379> For 10+ Quick Drops Daily\n\n"
            f"Make Sure To Apply For Staff In 📋 <#1409892318701551666>"
        ),
        color=discord.Color.teal()
    )

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Member #{member.guild.member_count}")

    await channel.send(
        content=f"Hello {member.mention}",
        embed=embed
    )

@bot.tree.command(
    name="giveaway",
    description="Start a giveaway with a join button",
    guild=MY_GUILD
)
@app_commands.checks.has_role("Staff")
async def giveaway(interaction: discord.Interaction, prize: str, duration: str, winners: int):
    participants = []

    # Parse duration
    try:
        duration_seconds = parse_duration(duration)
    except ValueError as e:
        await interaction.response.send_message(str(e), ephemeral=True)
        return

    end_time = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)
    end_timestamp = int(end_time.timestamp())

    embed = discord.Embed(
        title="🎉 Giveaway Started! 🎉",
        description=(
            f"🎁 **Prize:** {prize}\n"
            f"⏰ **Ends:** <t:{end_timestamp}:R>\n"
            f"🏆 **Winners:** {winners}\n"
            f"👥 **Entries:** 0"
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Started by {interaction.user}")

    class GiveawayView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=duration_seconds)

        @discord.ui.button(label="Join", style=discord.ButtonStyle.green, emoji="🎉")
        async def join_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
            if button_interaction.user not in participants:
                participants.append(button_interaction.user)
                embed.description = (
                    f"🎁 **Prize:** {prize}\n"
                    f"⏰ **Ends:** <t:{end_timestamp}:R>\n"
                    f"🏆 **Winners:** {winners}\n"
                    f"👥 **Entries:** {len(participants)}"
                )
                await interaction.edit_original_response(embed=embed, view=view)
                await button_interaction.response.send_message("You joined the giveaway!", ephemeral=True)
            else:
                await button_interaction.response.send_message("You have already joined!", ephemeral=True)

    view = GiveawayView()
    await interaction.response.send_message(embed=embed, view=view)

    # Odotetaan duration
    await asyncio.sleep(duration_seconds)

    # Disabloi nappi
    for item in view.children:
        item.disabled = True
    await interaction.edit_original_response(view=view)

    # Pick winners ja lähetä samaan kanavaan
    if participants:
        if winners > len(participants):
            winners = len(participants)
        giveaway_winners = random.sample(participants, winners)
        winner_mentions = " ".join(w.mention for w in giveaway_winners)
        await interaction.channel.send(
            f"🎉 **Giveaway Ended!** 🎉\n"
            f"Congratulations {winner_mentions}!\n"
            f"You won **{prize}** 🎁\n"
            f"Please create a ticket in <#1399019189729099909> to claim your prize!"
            # ticket channel
        )
    else:
        await interaction.channel.send(
            f"🎉 **Giveaway Ended!** 🎉\nNo one joined the giveaway for **{prize}** 😢"
        )

#filter

import re

STAFF_ROLES = [
    "Staff",
    "🚨Moderator🚨",
    "🛡️Admin🛡️",
    "OrcxYT👑",
    "⚒️SrHelper",
    "🗡️DEV🗡️",
    "💸Manager💸",
    "💸 Staff Manager 💸",
    "⚓Helper",
    "Ticket staff",
    "🥳Giveaway Manager🥳",
    "Partner Manager",
    "💸Staff Manager Trainee",
    "🛠️Junior Admin",
    "SrMod"
]

BANNED_WORDS = [
    "nigger",
    "niga",
    "kys",
    "fuck",
    "bitch",
    "asshole",
    "dick",
    "dickhead",
    "ass",
    "nigga",
    "bitchass",
    "bitchassniga",
    "motherfucker",
    "mother-fucker",
    "nigg",
    "kys",
    "nigger",
    "nig",
    "killyourself",
    "tits",
    "balls",
    "twat",
    "arsehead",
    "arsehole",
    "bastard",
    "bollocks",
    "brotherfucker",
    "child-fucker",
    "cocksucker",
    "cunt",
    "dick-head",
    "dickhead",
    "dumb-ass",
    "dumbass",
    "father-fucker",
    "fatherfucker",
    "wanker"
]

BANNED_PHRASES = [
    "kill yourself",
    "go die",
    "you should die",
    "bitch ass niga"
]

word_pattern = re.compile(
    r"\b(" + "|".join(map(re.escape, BANNED_WORDS)) + r")\b",
    re.IGNORECASE
)

phrase_pattern = re.compile(
    r"\b(" + "|".join(map(re.escape, BANNED_PHRASES)) + r")\b",
    re.IGNORECASE
)

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if not isinstance(message.author, discord.Member):
        return

    # 🔒 Staff bypass
    if any(role.name in STAFF_ROLES for role in message.author.roles):
        await bot.process_commands(message)
        return

    content = message.content

    if word_pattern.search(content) or phrase_pattern.search(content):
        await message.delete()

        member = message.author
        user_id = str(member.id)
        now = datetime.utcnow()
        current_month = now.strftime("%Y-%m")

        if user_id not in WARNINGS or WARNINGS[user_id]["month"] != current_month:
            WARNINGS[user_id] = {
                "month": current_month,
                "count": 0
            }

        WARNINGS[user_id]["count"] += 1
        warn_count = WARNINGS[user_id]["count"]
        save_warnings(WARNINGS)

        # 📢 Kanava-ilmoitus
        await message.channel.send(
            f"⚠️ {member.mention}, inappropriate language is not allowed.\n"
            f"Warnings: **{warn_count}/{BAN_AT_WARN}**",
            delete_after=6
        )

        # 📩 DM käyttäjälle
        try:
            await member.send(
                f"⚠️ **Automatic Warning**\n\n"
                f"Server: **{message.guild.name}**\n"
                f"Reason: Inappropriate language\n"
                f"Warnings this month: **{warn_count}/{BAN_AT_WARN}**"
            )
        except discord.Forbidden:
            pass

        # 🔇 AUTO MUTE (3 warnings)
        if warn_count == MUTE_AT_WARN:
            try:
                until = datetime.utcnow() + MUTE_DURATION
                await member.timeout(until, reason="Reached 3 warnings")
                await message.channel.send(
                    f"🔇 {member.mention} has been **muted for 7 days** (3 warnings)."
                )
            except discord.Forbidden:
                pass

        # 🔨 AUTO BAN (5 warnings)
        elif warn_count >= BAN_AT_WARN:
            try:
                await member.ban(reason="Reached 5 warnings in one month")
                await message.channel.send(
                    f"🔨 {member.mention} has been **banned** (5 warnings)."
                )
            except discord.Forbidden:
                pass

        return

    await bot.process_commands(message)

# --- Rock Paper Scissors (global slash command) ---
@bot.tree.command(
    name="rps",
    description="Play Rock, Paper, Scissors with the bot"
)
@app_commands.describe(
    choice="Your choice: rock, paper, or scissors"
)
async def rps(interaction: discord.Interaction, choice: str):
    choice = choice.lower()
    if choice not in ["rock", "paper", "scissors"]:
        await interaction.response.send_message(
            "Invalid choice! Choose rock, paper, or scissors.", ephemeral=True
        )
        return

    bot_choice = random.choice(["rock", "paper", "scissors"])

    if choice == bot_choice:
        result = "It's a tie!"
        color = discord.Color.greyple()
    elif (
        (choice == "rock" and bot_choice == "scissors") or
        (choice == "paper" and bot_choice == "rock") or
        (choice == "scissors" and bot_choice == "paper")
    ):
        result = "You win!"
        color = discord.Color.green()
    else:
        result = "You lose!"
        color = discord.Color.red()

    embed = discord.Embed(
        title="🎮 Rock, Paper, Scissors",
        color=color
    )
    embed.add_field(name="Your choice", value=choice.capitalize(), inline=True)
    embed.add_field(name="Bot's choice", value=bot_choice.capitalize(), inline=True)
    embed.add_field(name="Result", value=result, inline=False)
    embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)

    # user_id -> { "YYYY-MM": warn_count }

@bot.command(name="warn")
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason: str):
    if any(role.name in STAFF_ROLES for role in member.roles):
        await ctx.send("❌ You cannot warn a staff member.")
        return

    now = datetime.utcnow()
    current_month = now.strftime("%Y-%m")
    user_id = str(member.id)

    if user_id not in WARNINGS or WARNINGS[user_id]["month"] != current_month:
        WARNINGS[user_id] = {
            "month": current_month,
            "count": 0
        }

    WARNINGS[user_id]["count"] += 1
    save_warnings(WARNINGS)

    warn_count = WARNINGS[user_id]["count"]

    # 📩 DM
    try:
        await member.send(
            f"⚠️ **You have received a warning**\n\n"
            f"Server: **{ctx.guild.name}**\n"
            f"Reason: **{reason}**\n"
            f"Warnings this month: **{warn_count}/{BAN_AT_WARN}**"
        )
    except discord.Forbidden:
        pass

    await ctx.send(
        f"⚠️ {member.mention} warned.\n"
        f"Reason: **{reason}**\n"
        f"Warnings: **{warn_count}/{BAN_AT_WARN}**"
    )

    # 🔇 AUTO MUTE (3 warnings)
    if warn_count == MUTE_AT_WARN:
        until = datetime.utcnow() + MUTE_DURATION
        await member.timeout(until, reason="Reached 3 warnings")

        await ctx.send(
            f"🔇 {member.mention} muted for **7 days** (3 warnings)."
        )

        try:
            await member.send(
                "🔇 **You have been muted**\n"
                "Reason: 3 warnings in one month\n"
                "Duration: 7 days"
            )
        except discord.Forbidden:
            pass

    # 🔨 AUTO BAN (5 warnings)
    elif warn_count >= BAN_AT_WARN:
        await member.ban(reason="Reached 5 warnings in one month")
        await ctx.send(
            f"🔨 {member.mention} banned for too many warnings."
        )

@warn.error
async def warn_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: !warn @user <reason>")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid user. Mention the user correctly.")
    else:
        await ctx.send(f"❌ Error: {error}")

@bot.command(name="warnings")
@commands.has_permissions(moderate_members=True)
async def warnings(ctx, member: discord.Member):
    user_id = str(member.id)
    current_month = datetime.utcnow().strftime("%Y-%m")

    if user_id not in WARNINGS or WARNINGS[user_id]["month"] != current_month:
        count = 0
    else:
        count = WARNINGS[user_id]["count"]

    await ctx.send(
        f"📋 **Warnings for {member}**\n"
        f"This month: **{count}/{MAX_WARNS_PER_MONTH}**"
    )

@bot.command(name="clearwarns")
@commands.has_permissions(administrator=True)
async def clearwarns(ctx, member: discord.Member):
    WARNINGS.pop(str(member.id), None)
    save_warnings(WARNINGS)
    await ctx.send(f"✅ Cleared warnings for {member.mention}.")

# --- Run bot ---
bot.run(token, log_handler=handler, log_level=logging.DEBUG)