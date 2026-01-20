class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    async def ban(self, ctx, member: discord.Member, *, reason="No reason"):
        if not any(r.id == STAFF_ROLE_ID for r in ctx.author.roles):
            return

        await member.ban(reason=reason)

        async with aiosqlite.connect("bot.db") as db:
            await db.execute(
                "INSERT INTO mod_logs (action, target_id, staff_id, reason, timestamp) VALUES (?, ?, ?, ?, ?)",
                ("ban", member.id, ctx.author.id, reason, int(time.time()))
            )
            await db.commit()

        await ctx.send(f"🔨 {member} banned")

    @commands.command(name="unban")
    async def unban(self, ctx, user_id: int):
        if not any(r.id == STAFF_ROLE_ID for r in ctx.author.roles):
            return

        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)

        await ctx.send(f"♻️ {user} unbanned")

async def setup(bot):
    await bot.add_cog(Ban(bot))
