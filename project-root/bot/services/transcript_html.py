import discord
from datetime import datetime

async def build_html_transcript(channel: discord.TextChannel):
    messages = []
    async for msg in channel.history(oldest_first=True):
        messages.append(f"""
        <div class="msg">
            <b>{msg.author}</b>
            <span class="time">{msg.created_at}</span><br>
            {msg.content}
        </div>
        """)

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial; background: #111; color: #eee; }}
            .msg {{ margin-bottom: 10px; }}
            .time {{ color: #999; font-size: 12px; }}
        </style>
    </head>
    <body>
        <h2>Transcript: {channel.name}</h2>
        {''.join(messages)}
    </body>
    </html>
    """

    filename = f"{channel.name}-{datetime.utcnow().timestamp()}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    return filename
