from .modals import CloseReasonModal
from views.ticket_close_view import CloseReasonModal
from services.sla_service import start_sla, end_sla
from services.staff_stats import log_ticket_close
from services.sla_service import end_sla_seconds, format_duration

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

        async def auto_claim(self, member: discord.Member, channel: discord.TextChannel):
            if self.claimed_by is not None:
                return

            if not any(r.id == STAFF_ROLE_ID for r in member.roles):
                return

            self.claimed_by = member.id
            await channel.send(f"📌 Automatically claimed by {member.mention}")

        async with aiosqlite.connect("bot.db") as db:
            await db.execute(
                "UPDATE ticket_stats SET claimed_by = ? WHERE channel_id = ?",
                (interaction.user.id, interaction.channel.id)
            )
            await db.commit()

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
    async def close(self, interaction: discord.Interaction, _):
        if not any(r.id == STAFF_ROLE_ID for r in interaction.user.roles):
            await interaction.response.send_message("❌ Staff only.", ephemeral=True)
            return

        await interaction.response.send_modal(
            CloseReasonModal(self)
        )

    async def final_close(self, interaction, reason: str):
        duration = end_sla(self.opened_at)
        seconds = end_sla_seconds(self.opened_at)
        await log_ticket_close(interaction.user.id, seconds)

        duration = format_duration(seconds)

        log_embed = discord.Embed(
            title="🔒 Ticket Closed",
            color=discord.Color.red()
        )
        log_embed.add_field(name="Closed by", value=interaction.user.mention)
        log_embed.add_field(name="Reason", value=reason, inline=False)
        log_embed.add_field(name="Open time", value=duration)

        log_channel = interaction.guild.get_channel(TRANSCRIPT_LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(embed=log_embed)

        await interaction.channel.send(
            embed=log_embed,
            view=ReopenView()
        )

        await interaction.channel.edit(
            name=f"closed-{interaction.channel.name}",
            locked=True
        )

            # 📜 Transcript
            messages = []
            async for msg in channel.history(oldest_first=True):
                messages.append(
                    f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}] "
                    f"{msg.author}: {msg.content}"
                )

            transcript_text = "\n".join(messages)
            transcript_file = discord.File(
                io.StringIO(transcript_text),
                filename=f"{channel.name}-transcript.txt"
            )

            # 📌 Log embed
            log_embed = discord.Embed(
                title="🔒 Ticket Closed",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            log_embed.add_field(name="Closed by", value=interaction.user.mention, inline=False)
            log_embed.add_field(name="Owner", value=f"<@{self.owner_id}>", inline=False)
            log_embed.add_field(name="Reason", value=reason, inline=False)
            log_embed.add_field(name="Channel", value=channel.name, inline=False)

            log_channel = guild.get_channel(TRANSCRIPT_LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(embed=log_embed, file=transcript_file)

            # 📩 DM käyttäjälle
            owner = guild.get_member(self.owner_id)
            if owner:
                try:
                    dm = discord.Embed(
                        title="🎫 Your ticket has been closed",
                        color=discord.Color.red()
                    )
                    dm.add_field(name="Server", value=guild.name, inline=False)
                    dm.add_field(name="Reason", value=reason, inline=False)
                    dm.add_field(name="Closed by", value=interaction.user.name, inline=False)

                    await owner.send(embed=dm)
                except discord.Forbidden:
                    pass

            await channel.delete()

        # 🗑 Poista kanava
        await interaction.channel.delete()