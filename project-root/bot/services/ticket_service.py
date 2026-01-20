import discord
import io
from datetime import datetime
from bot.config.settings import (
    TICKET_CATEGORY_ID,
    TICKET_LOG_CHANNEL_ID,
    STAFF_ROLE_ID
)


async def create_ticket_channel(
    interaction: discord.Interaction,
    ticket_type: str,
    embed: discord.Embed
) -> discord.TextChannel:

    guild = interaction.guild
    category = guild.get_channel(TICKET_CATEGORY_ID)

    if not isinstance(category, discord.CategoryChannel):
        raise RuntimeError("Ticket category not found")

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )
    }

    staff_role = guild.get_role(STAFF_ROLE_ID)
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            manage_channels=True
        )

    channel = await guild.create_text_channel(
        name=f"{ticket_type}-{interaction.user.id}",
        category=category,
        overwrites=overwrites
    )

    await channel.send(
        content=interaction.user.mention,
        embed=embed
    )

    return channel


async def close_ticket(
    channel: discord.TextChannel,
    closed_by: discord.Member,
    reason: str,
    owner_id: int
):
    messages = []
    async for msg in channel.history(oldest_first=True):
        messages.append(
            f"[{msg.created_at:%Y-%m-%d %H:%M}] {msg.author}: {msg.content}"
        )

    transcript = "\n".join(messages)
    file = discord.File(
        io.StringIO(transcript),
        filename=f"{channel.name}-transcript.txt"
    )

    log_channel = channel.guild.get_channel(TICKET_LOG_CHANNEL_ID)

    embed = discord.Embed(
        title="🔒 Ticket Closed",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Channel", value=channel.name)
    embed.add_field(name="Closed by", value=closed_by.mention)
    embed.add_field(name="Reason", value=reason)

    if log_channel:
        await log_channel.send(embed=embed, file=file)

    owner = channel.guild.get_member(owner_id)
    if owner:
        try:
            await owner.send(
                f"🎫 Your ticket **{channel.name}** was closed.\n"
                f"Reason: **{reason}**"
            )
        except discord.Forbidden:
            pass

    await channel.delete()
