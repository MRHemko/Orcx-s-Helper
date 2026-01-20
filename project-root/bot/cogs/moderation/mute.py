import discord, time, aiosqlite
from discord.ext import commands, tasks
from config import MUTED_ROLE_ID, MOD_LOG_CHANNEL_ID, STAFF_ROLE_ID

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.unmute_task.start()

    @commands.command(name="mute")
    async def mute(self, ctx, member: discord.Member, duration: int, *, reason="No reason"):
        if not any(r.id == STAFF_ROLE_ID for r in ctx.author.roles):
            return

        muted_role = ctx.guild.get_role(MUTED_ROLE_ID)
        await member.add_roles(muted_role)

        unmute_at = int(time.time()) + duration

        async with aiosqlite.connect("bot.db") as db:
            await db.execute(
                "INSERT INTO mutes VALUES (?, ?, ?)",
                (member.id, ctx.guild.id, unmute_at)
            )
            await db.execute(
                "INSERT INTO mod_logs (action, target_id, staff_id, reason, timestamp) VALUES (?, ?, ?, ?, ?)",
                ("mute", member.id, ctx.author.id, reason, int(time.time()))
            )
            await db.commit()

        await ctx.send(f"🔇 {member.mention} muted for {duration}s")

    @commands.command(name="unmute")
    async def unmute(self, ctx, member: discord.Member):
        if not any(r.id == STAFF_ROLE_ID for r in ctx.author.roles):
            return

        muted_role = ctx.guild.get_role(MUTED_ROLE_ID)
        await member.remove_roles(muted_role)

        async with aiosqlite.connect("bot.db") as db:
            await db.execute(
                "DELETE FROM mutes WHERE user_id = ? AND guild_id = ?",
                (member.id, ctx.guild.id)
            )
            await db.commit()

        await ctx.send(f"🔊 {member.mention} unmuted")

    @tasks.loop(seconds=30)
    async def unmute_task(self):
        now = int(time.time())

        async with aiosqlite.connect("bot.db") as db:
            cursor = await db.execute(
                "SELECT user_id, guild_id FROM mutes WHERE unmute_at <= ?",
                (now,)
            )
            rows = await cursor.fetchall()

            for user_id, guild_id in rows:
                guild = self.bot.get_guild(guild_id)
                member = guild.get_member(user_id)
                if member:
                    muted_role = guild.get_role(MUTED_ROLE_ID)
                    await member.remove_roles(muted_role)

                await db.execute(
                    "DELETE FROM mutes WHERE user_id = ? AND guild_id = ?",
                    (user_id, guild_id)
                )

            await db.commit()

async def setup(bot):
    await bot.add_cog(Mute(bot))
