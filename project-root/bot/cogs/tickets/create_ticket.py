import discord
from bot.config import *
from .manage import TicketManageView
from bot.database.tickets import DB
from datetime import datetime

async def create_ticket(DB, user_id, category):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """
            INSERT INTO ticket_stats
                (channel_id, owner_id, ticket_type, opened_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                channel.id,
                interaction.user.id,
                ticket_type,
                datetime.utcnow().isoformat()
            )
        )
        await db.commit()

async def create_ticket(
    interaction: discord.Interaction,
    ticket_type: str,
    embed: discord.Embed
):
    guild = interaction.guild
    category = guild.get_channel(TICKET_CATEGORY_ID)

    if category is None or not isinstance(category, discord.CategoryChannel):
        raise RuntimeError("Ticket category not found or invalid")

    # 🔐 Oikeudet
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )
    }

    staff_role_id = STAFF_PINGS.get(ticket_type)
    if staff_role_id:
        staff_role = guild.get_role(staff_role_id)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True
            )

    channel_name = f"{ticket_type}-{interaction.user.id}"

    channel = await guild.create_text_channel(
        name=channel_name,
        category=category,
        overwrites=overwrites
    )

    # 📌 Lähetä ticketin sisältö
    staff_ping = ""
    staff_role_id = STAFF_PINGS.get(ticket_type)

    if staff_role_id:
        staff_role = guild.get_role(staff_role_id)
        if staff_role:
            staff_ping = staff_role.mention

    await channel.send(
        content=f"{staff_ping}\n{interaction.user.mention}",
        embed=embed,
        view=TicketManageView(interaction.user.id),
        allowed_mentions=discord.AllowedMentions(
            everyone=False,
            roles=True,
            users=True
        )
    )

    # ✅ Vastaa interactioniin (MODAL SAFE)
    await interaction.followup.send(
        f"✅ Ticket created: {channel.mention}",
        ephemeral=True
    )