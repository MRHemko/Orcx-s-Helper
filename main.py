import discord
from discord.ext import commands, tasks
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
import io

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

DAILY_FILE = Path("daily.json")

def load_daily():
    if DAILY_FILE.exists():
        with open(DAILY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "message_id": None,
        "end_time": None,
        "participants": []
    }

def save_daily(data):
    with open(DAILY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

DAILY_DATA = load_daily()

DAILY_GIVEAWAY_CHANNEL_ID = 1400833986934210634
DAILY_PRIZE = "🎁 3.000.000 on DonutSMP"
DAILY_WINNERS = 1
DAILY_DURATION = 86400

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

async def start_daily_giveaway():
    channel = await bot.fetch_channel(DAILY_GIVEAWAY_CHANNEL_ID)
    if channel is None:
        return

    participants = [
        bot.get_user(int(uid))
        for uid in DAILY_DATA.get("participants", [])
        if bot.get_user(int(uid)) is not None
    ]

    end_time = datetime.now(timezone.utc) + timedelta(seconds=DAILY_DURATION)
    end_timestamp = int(end_time.timestamp())

    embed = discord.Embed(
        title="🎉 DAILY GIVEAWAY 🎉",
        description=(
            f"🎁 **Prize:** {DAILY_PRIZE}\n"
            f"⏰ **Ends:** <t:{end_timestamp}:R>\n"
            f"🏆 **Winners:** {DAILY_WINNERS}\n"
            f"👥 **Entries:** {len(participants)}"
        ),
        color=discord.Color.gold()
    )

    class DailyView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=DAILY_DURATION)

        @discord.ui.button(label="Join", style=discord.ButtonStyle.green, emoji="🎉")
        async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
            if str(interaction.user.id) not in DAILY_DATA["participants"]:
                DAILY_DATA["participants"].append(str(interaction.user.id))
                save_daily(DAILY_DATA)

                participants.append(interaction.user)

                embed.description = (
                    f"🎁 **Prize:** {DAILY_PRIZE}\n"
                    f"⏰ **Ends:** <t:{end_timestamp}:R>\n"
                    f"🏆 **Winners:** {DAILY_WINNERS}\n"
                    f"👥 **Entries:** {len(participants)}"
                )
                await interaction.message.edit(embed=embed, view=self)
                await interaction.response.send_message(
                    "You joined the daily giveaway!", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "You already joined!", ephemeral=True
                )

    view = DailyView()
    msg = await channel.send(embed=embed, view=view)

    # ✅ tallenna daily state OIKEASSA kohdassa
    DAILY_DATA["message_id"] = msg.id
    DAILY_DATA["end_time"] = end_timestamp
    if "participants" not in DAILY_DATA:
        DAILY_DATA["participants"] = []
    save_daily(DAILY_DATA)

    await asyncio.sleep(DAILY_DURATION)

    for item in view.children:
        item.disabled = True
    await msg.edit(view=view)

    if participants:
        winner = random.choice(participants)
        await channel.send(
            f"🎉 **Daily Giveaway Ended!** 🎉\n"
            f"Winner: {winner.mention}\n"
            f"Prize: **{DAILY_PRIZE}**\n"
            f"Please create a ticket in <#1399019189729099909> to claim your prize!"
        )
    else:
        await channel.send("😢 No one joined today's daily giveaway.")

    # ✅ tyhjennä daily.json VASTA lopussa
    DAILY_DATA.clear()
    DAILY_DATA.update({
        "message_id": None,
        "end_time": None,
        "participants": []
    })
    save_daily(DAILY_DATA)

@tasks.loop(hours=24)
async def daily_giveaway_task():
    await start_daily_giveaway()

@daily_giveaway_task.before_loop
async def before_daily():
    await bot.wait_until_ready()

    @bot.event
    async def on_ready():
        await bot.add_cog(TicketPanel(bot))
        await bot.tree.sync(guild=MY_GUILD)
        print("TicketPanel loaded")

    if not daily_giveaway_task.is_running():
        daily_giveaway_task.start()

    # ⛔ estä tupla daily
    if DAILY_DATA.get("end_time"):
        now = int(datetime.now(timezone.utc).timestamp())
        if now < DAILY_DATA["end_time"]:
            print("Daily giveaway already running, skipping start.")
            return

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
@app_commands.checks.has_role("Giveaway")
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
    "SrMod",
    "Giveaway"
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
        description="Play Rock, Paper, Scissors with the bot",
        guild=MY_GUILD
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

# =========================
# CONFIG
# =========================

TICKET_FORUM_ID = 1399019189729099909
TRANSCRIPT_LOG_CHANNEL_ID = 1444618133448032388

SUPPORT_ROLE_ID = 1456322413259133173
PARTNER_ROLE_ID = 1456322513637212373
STAFF_ROLE_ID = 1444614803518914752

STAFF_PINGS = {
    "support": SUPPORT_ROLE_ID,
    "partner": PARTNER_ROLE_ID,
    "market": STAFF_ROLE_ID,
    "sponsor_giveaway": STAFF_ROLE_ID,
    "giveaway_claim": STAFF_ROLE_ID,
    "media": STAFF_ROLE_ID
}

TICKET_TAGS = {
    "support": 1457710146124910735,
    "partner": 1457710400287146024,
    "market": 1457710189196087378,
    "sponsor_giveaway": 1457710275003158669,
    "giveaway_claim": 1457710230761771072,
    "media": 1457710338882535648
}

TICKET_TYPES = {
    "support": "🛠 Support",
    "partner": "🤝 Partner",
    "market": "🛒 Market",
    "sponsor_giveaway": "💰 Sponsor Giveaway",
    "giveaway_claim": "🎁 Giveaway Claim",
    "media": "🎥 Media"
}

# =========================
# MODALS
# =========================

class SupportModal(discord.ui.Modal, title="Support Ticket"):
    reason = discord.ui.TextInput(label="Why do you need support?", required=True)
    ign = discord.ui.TextInput(label="IGN (if refund)", required=False)
    amount = discord.ui.TextInput(label="Amount owed (if refund)", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🛠 Support Ticket", color=discord.Color.blurple())
        embed.add_field(name="Reason", value=self.reason.value, inline=False)
        embed.add_field(name="IGN", value=self.ign.value or "N/A")
        embed.add_field(name="Amount", value=self.amount.value or "N/A")

        await create_ticket(interaction, "support", embed)


class PartnerModal(discord.ui.Modal, title="Partner Application"):
    members = discord.ui.TextInput(label="How many members does your server have?")
    read = discord.ui.TextInput(label="Have you read partner requirements?")
    donut = discord.ui.TextInput(label="Is your server DonutSMP related?")
    rules = discord.ui.TextInput(label="Does your server follow DonutSMP rules?")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🤝 Partner Application", color=discord.Color.green())
        embed.add_field(name="Members", value=self.members.value)
        embed.add_field(name="Read Requirements", value=self.read.value)
        embed.add_field(name="DonutSMP Related", value=self.donut.value)
        embed.add_field(name="Follows Rules", value=self.rules.value)

        await create_ticket(interaction, "partner", embed)


class MarketModal(discord.ui.Modal, title="Market Ticket"):
    buy_sell = discord.ui.TextInput(label="Buying or selling?")
    prices = discord.ui.TextInput(label="Have you read spawner prices?")
    amount = discord.ui.TextInput(label="How many?")
    spawner = discord.ui.TextInput(label="Spawner type?")
    agree = discord.ui.TextInput(label="Agree scamming = ban?")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🛒 Market Ticket", color=discord.Color.gold())
        embed.add_field(name="Type", value=self.buy_sell.value)
        embed.add_field(name="Prices Read", value=self.prices.value)
        embed.add_field(name="Amount", value=self.amount.value)
        embed.add_field(name="Spawner", value=self.spawner.value)
        embed.add_field(name="Agreement", value=self.agree.value)

        await create_ticket(interaction, "market", embed)


class SponsorModal(discord.ui.Modal, title="Sponsor Giveaway"):
    amount = discord.ui.TextInput(label="How much do you sponsor?")
    ign = discord.ui.TextInput(label="Your IGN")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="💰 Sponsor Giveaway", color=discord.Color.purple())
        embed.add_field(name="Amount", value=self.amount.value)
        embed.add_field(name="IGN", value=self.ign.value)

        await create_ticket(interaction, "sponsor_giveaway", embed)


class MediaModal(discord.ui.Modal, title="Media Ticket"):
    ign = discord.ui.TextInput(label="Your IGN")
    proof = discord.ui.TextInput(label="Proof of MC ownership", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎥 Media Ticket", color=discord.Color.teal())
        embed.add_field(name="IGN", value=self.ign.value)
        embed.add_field(name="Proof", value=self.proof.value)

        await create_ticket(interaction, "media", embed)

# =========================
# GIVEAWAY CLAIM FLOW
# =========================#

class GiveawayClaimView(discord.ui.View):
    timeout = 300

    def __init__(self, guild: discord.Guild):
        super().__init__()

        channel_select = self.children[0]
        channel_select.options = [
            discord.SelectOption(label=ch.name, value=str(ch.id))
            for ch in guild.text_channels
            if "giveaway" in ch.name.lower()
        ]

    @discord.ui.select(
        placeholder="Select giveaway channel",
        min_values=1,
        max_values=1,
        options=[],  # täytetään dynaamisesti
        custom_id="giveaway_channel"
    )
    async def select_channel(self, interaction: discord.Interaction, select: discord.ui.Select):
        channel_id = int(select.values[0])
        channel = interaction.guild.get_channel(channel_id)

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                "❌ Please select a text channel.",
                ephemeral=True
            )
            return

        self.channel = channel
        await interaction.response.defer(ephemeral=True)

    @discord.ui.select(
        placeholder="Select giveaway host (staff)",
        min_values=1,
        max_values=1,
        options=[],
        custom_id="giveaway_host"
    )
    async def select_host(self, interaction: discord.Interaction, select: discord.ui.Select):
        member_id = int(select.values[0])
        member = interaction.guild.get_member(member_id)

        if not member or not any(r.id == STAFF_ROLE_ID for r in member.roles):
            await interaction.response.send_message(
                "❌ Selected user is not staff.",
                ephemeral=True
            )
            return

        self.host = member
        await interaction.response.defer(ephemeral=True)

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.success)
    async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.channel or not self.host:
            await interaction.response.send_message(
                "❌ Please select both channel and host.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            GiveawayClaimModal(self.channel, self.host)
        )

class GiveawayClaimModal(discord.ui.Modal, title="Giveaway Claim"):
    ign = discord.ui.TextInput(label="Your IGN")
    amount = discord.ui.TextInput(label="Prize amount")

    def __init__(self, guild: discord.Guild):
        super().__init__()

        channel_select = self.children[0]
        channel_select.options = [
            discord.SelectOption(label=ch.name, value=str(ch.id))
            for ch in guild.text_channels
            if "giveaway" in ch.name.lower()
        ]

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎁 Giveaway Claim", color=discord.Color.orange())
        embed.add_field(name="IGN", value=self.ign.value)
        embed.add_field(name="Amount", value=self.amount.value)
        embed.add_field(name="Channel", value=self.channel.mention)
        embed.add_field(name="Host", value=self.host.mention)

        await create_ticket(interaction, "giveaway_claim", embed)

# =========================
# CREATE TICKET
# =========================

async def create_ticket(interaction: discord.Interaction, ticket_type: str, embed: discord.Embed):
    forum: discord.ForumChannel = interaction.guild.get_channel(TICKET_FORUM_ID)

    applied_tags = []
    tag_id = TICKET_TAGS.get(ticket_type)
    if tag_id:
        tag = discord.utils.get(forum.available_tags, id=tag_id)
        if tag:
            applied_tags.append(tag)

    thread = await forum.create_thread(
        name=f"{TICKET_TYPES[ticket_type]} | {interaction.user}",
        content=interaction.user.mention,
        embed=embed,
        applied_tags=applied_tags
    )

    role_id = STAFF_PINGS.get(ticket_type)
    ping = f"<@&{role_id}>" if role_id else ""

    await thread.send(
        content=f"{ping}\n📌 **New ticket created**",
        view=TicketManageView(interaction.user.id)
    )

    await interaction.response.send_message(
        f"✅ Ticket created: {thread.mention}",
        ephemeral=True
    )

# =========================
# TICKET MANAGEMENT
# =========================

class TicketManageView(discord.ui.View):
    timeout = None

    def __init__(self, owner_id: int):
        super().__init__()
        self.owner_id = owner_id
        self.claimed_by = None

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(r.id == STAFF_ROLE_ID for r in interaction.user.roles):
            await interaction.response.send_message("❌ Staff only.", ephemeral=True)
            return

        self.claimed_by = interaction.user.id
        await interaction.channel.send(f"📌 Claimed by {interaction.user.mention}")
        await interaction.response.defer()

    @discord.ui.button(label="Unclaim", style=discord.ButtonStyle.gray)
    async def unclaim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.claimed_by:
            await interaction.response.send_message("❌ Only claimer.", ephemeral=True)
            return

        self.claimed_by = None
        await interaction.channel.send("❌ Ticket unclaimed")
        await interaction.response.defer()

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(r.id == STAFF_ROLE_ID for r in interaction.user.roles):
            await interaction.response.send_message("❌ Staff only.", ephemeral=True)
            return

        messages = []
        async for msg in interaction.channel.history(oldest_first=True):
            messages.append(f"[{msg.created_at}] {msg.author}: {msg.content}")

        transcript = "\n".join(messages)
        file = discord.File(io.StringIO(transcript), filename="transcript.txt")

        log = interaction.guild.get_channel(TRANSCRIPT_LOG_CHANNEL_ID)
        embed = discord.Embed(
            title="🔒 Ticket Closed",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Closed by", value=interaction.user.mention)
        embed.add_field(name="Owner", value=f"<@{self.owner_id}>")

        await log.send(embed=embed, file=file)
        await interaction.channel.delete()

# =========================
# PANEL
# =========================

class TicketPanelView(discord.ui.View):
    timeout = None

    @discord.ui.button(label="📩 Support", style=discord.ButtonStyle.primary)
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SupportModal())

    @discord.ui.button(label="🤝 Partner", style=discord.ButtonStyle.primary)
    async def partner(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PartnerModal())

    @discord.ui.button(label="🛒 Market", style=discord.ButtonStyle.secondary)
    async def market(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MarketModal())

    @discord.ui.button(label="🎁 Giveaway Claim", style=discord.ButtonStyle.success)
    async def giveaway_claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
    "Please provide giveaway details:", view=GiveawayClaimView(), ephemeral=True)

    @discord.ui.button(label="🎥 Media", style=discord.ButtonStyle.secondary)
    async def media(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MediaModal())

    @discord.ui.button(label="💰 Sponsor Giveaway", style=discord.ButtonStyle.success)
    async def sponsor(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SponsorModal())
# =========================
# EMBED
# =========================

embed = discord.Embed(
    title="🎫 Orcx's Ocean — Ticket Center",
    description=(
        "**Please choose the ticket type that best fits your request.**\n\n"

        "### 👷 Support\n"
        "> Need help with refunds, issues, or general questions?\n"
        "> Click **📩 Support** to contact our support team.\n\n"

        "### 🤝 Partnership\n"
        "> Interested in partnering with Orcx's Ocean?\n"
        "> Click **🤝 Partner** to submit a partnership request.\n\n"

        "### 🛒 Market\n"
        "> Want to sell spawners or make a market-related request?\n"
        "> Click **🛒 Market** to proceed.\n\n"

        "### 🎉 Giveaway Claim\n"
        "> Won a giveaway and need to claim your prize?\n"
        "> Click **🎁 Giveaway Claim** to continue.\n\n"

        "### 🎥 Media / VIP\n"
        "> Applying for Media or VIP?\n"
        "> Click **🎥 Media** to apply.\n\n"

        "### 💰 Sponsor Giveaway\n"
        "> Want to sponsor a giveaway for the community?\n"
        "> Click **💰 Sponsor Giveaway** to get started."
    ),
    color=discord.Color.blurple()
)
embed.set_footer(text="Orcx's Ocean • Support System")

# =========================
# COG
# =========================

class TicketPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketpanel", description="Send the ticket panel")
    async def ticketpanel(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=embed,
            view=TicketPanelView()
        )

async def setup(bot):
    await bot.add_cog(TicketPanel(bot))

@bot.command(name="ticketpanel")
@commands.has_permissions(administrator=True)
async def ticketpanel_prefix(ctx):
    embed = discord.Embed(
        title="🎫 Orcx's Ocean — Ticket Center",
        description=(
            "**Please choose the ticket type that best fits your request.**\n\n"

            "### 👷 Support\n"
            "> Need help with refunds, issues, or general questions?\n"
            "> Click **📩 Support** to contact our support team.\n\n"

            "### 🤝 Partnership\n"
            "> Interested in partnering with Orcx's Ocean?\n"
            "> Click **🤝 Partner** to submit a partnership request.\n\n"

            "### 🛒 Market\n"
            "> Want to sell spawners or make a market-related request?\n"
            "> Click **🛒 Market** to proceed.\n\n"

            "### 🎉 Giveaway Claim\n"
            "> Won a giveaway and need to claim your prize?\n"
            "> Click **🎁 Giveaway Claim** to continue.\n\n"

            "### 🎥 Media / VIP\n"
            "> Applying for Media or VIP?\n"
            "> Click **🎥 Media** to apply.\n\n"

            "### 💰 Sponsor Giveaway\n"
            "> Want to sponsor a giveaway for the community?\n"
            "> Click **💰 Sponsor Giveaway** to get started."
        ),
        color=discord.Color.blurple()
    )

    embed.set_footer(text="Orcx's Ocean • Support System")
    await ctx.send(embed=embed, view=TicketPanelView())

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