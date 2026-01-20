import discord
from discord import app_commands
from datetime import datetime
import aiosqlite
from config import TICKET_CATEGORY_ID, TICKET_LOG_CHANNEL_ID, STAFF_ROLE_IDS
from utils.transcript import generate_transcript
from config import TRANSCRIPT_LOG_CHANNEL_ID

DB_PATH = "bot.db"

def is_staff(member: discord.Member):
    return any(r.id in STAFF_ROLE_IDS for r in member.roles)

def setup(bot):

    # 🎟 Ticket creation button
    class TicketView(discord.ui.View):
        timeout = None

        @discord.ui.button(label="🎟 Open Ticket", style=discord.ButtonStyle.green)
        async def open(self, interaction: discord.Interaction, button):
            guild = interaction.guild
            category = guild.get_channel(TICKET_CATEGORY_ID)

            channel = await guild.create_text_channel(
                name=f"ticket-{interaction.user.name}",
                category=category
            )

            await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
            for role_id in STAFF_ROLE_IDS:
                role = guild.get_role(role_id)
                if role:
                    await channel.set_permissions(role, read_messages=True, send_messages=True)

            await channel.send(
                f"{interaction.user.mention} welcome!\n"
                "A staff member will assist you shortly."
            )

            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute(
                    "INSERT INTO tickets VALUES (?, ?, ?, ?, ?)",
                    (channel.id, interaction.user.id, None, "open", datetime.utcnow().isoformat())
                )
                await db.commit()

            await interaction.response.send_message(
                "✅ Ticket created!", ephemeral=True
            )

    @bot.tree.command(name="ticketpanel")
    async def ticketpanel(interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎟 Support Tickets",
            description="Click below to open a ticket",
            color=discord.Color.green()
        )
        await interaction.channel.send(embed=embed, view=TicketView())
        await interaction.response.send_message("Panel sent.", ephemeral=True)

    # 📌 Claim ticket
    @bot.tree.command(name="claim", description="Claim a ticket")
    async def claim(interaction: discord.Interaction):
        if not is_staff(interaction.user):
            return await interaction.response.send_message("❌ Staff only.", ephemeral=True)

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE tickets SET claimed_by = ? WHERE channel_id = ?",
                (interaction.user.id, interaction.channel.id)
            )
            await db.commit()

        await interaction.response.send_message(
            f"📌 Ticket claimed by {interaction.user.mention}"
        )

@bot.tree.command(name="close", description="Close ticket with reason")
async def close(interaction: discord.Interaction, reason: str):
    if not is_staff(interaction.user):
        return await interaction.response.send_message("❌ Staff only.", ephemeral=True)

    channel = interaction.channel
    guild = interaction.guild

    await interaction.response.defer()

    # 📄 Transcript
    transcript_file = await generate_transcript(channel)

    # 📌 Log-kanava
    log_channel = guild.get_channel(TRANSCRIPT_LOG_CHANNEL_ID)

    embed = discord.Embed(
        title="🎟 Ticket Closed",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Channel", value=channel.name, inline=False)
    embed.add_field(name="Closed by", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)

    if log_channel:
        await log_channel.send(embed=embed, file=transcript_file)

    # 📩 DM käyttäjälle
    try:
        async for member in channel.members:
            if not is_staff(member):
                dm = discord.Embed(
                    title="🎫 Your ticket has been closed",
                    description=f"Reason: **{reason}**",
                    color=discord.Color.red()
                )
                await member.send(embed=dm, file=transcript_file)
    except:
        pass

    await db.execute(
        """
        INSERT INTO ticket_stats (user_id, staff_id, action, created_at)
        VALUES (?, ?, 'close', ?)
        """,
        (member.id, interaction.user.id, datetime.utcnow().isoformat())
    )

    await channel.delete()

@bot.tree.command(name="ticketstats", description="View ticket statistics")
async def ticketstats(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user

    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM ticket_stats WHERE user_id = ? AND action = 'open'",
            (user.id,)
        )
        (opened,) = await cursor.fetchone()

        cursor = await db.execute(
            "SELECT COUNT(*) FROM ticket_stats WHERE staff_id = ? AND action = 'close'",
            (user.id,)
        )
        (closed,) = await cursor.fetchone()

    embed = discord.Embed(
        title="🎟 Ticket Statistics",
        color=discord.Color.blue()
    )
    embed.add_field(name="User", value=user.mention, inline=False)
    embed.add_field(name="Tickets Opened", value=str(opened), inline=True)
    embed.add_field(name="Tickets Closed (Staff)", value=str(closed), inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ticketleaderboard", description="Top staff by closed tickets")
@app_commands.checks.has_permissions(manage_guild=True)
async def ticketleaderboard(interaction: discord.Interaction):

    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("""
            SELECT staff_id, COUNT(*) as total
            FROM ticket_stats
            WHERE action = 'close'
            GROUP BY staff_id
            ORDER BY total DESC
            LIMIT 10
        """)
        rows = await cursor.fetchall()

    if not rows:
        return await interaction.response.send_message(
            "No ticket stats yet.", ephemeral=True
        )

    embed = discord.Embed(
        title="🏆 Ticket Staff Leaderboard",
        color=discord.Color.gold()
    )

    for i, (staff_id, total) in enumerate(rows, start=1):
        embed.add_field(
            name=f"#{i}",
            value=f"<@{staff_id}> — **{total}** tickets closed",
            inline=False
        )

    await interaction.response.send_message(embed=embed)
