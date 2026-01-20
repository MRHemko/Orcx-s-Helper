import discord
import io
from datetime import datetime

async def generate_transcript(channel: discord.TextChannel):
    lines = []

    async for msg in channel.history(oldest_first=True, limit=None):
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        author = f"{msg.author} ({msg.author.id})"
        content = msg.content or ""

        if msg.attachments:
            content += " " + " ".join(a.url for a in msg.attachments)

        lines.append(f"[{timestamp}] {author}: {content}")

    text = "\n".join(lines)

    return discord.File(
        io.StringIO(text),
        filename=f"{channel.name}-transcript.txt"
    )
