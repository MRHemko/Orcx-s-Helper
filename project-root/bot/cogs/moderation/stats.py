class ModStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    async def stats(self, ctx, member: discord.Member = None):
        if not any(r.id == STAFF_ROLE_ID for r in ctx.author.roles):
            return

        target = member or ctx.author

        async with aiosqlite.connect("bot.db") as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM mod_logs WHERE staff_id = ?",
                (target.id,)
            )
            (actions,) = await cursor.fetchone()

        embed = discord.Embed(
            title="📊 Moderation Stats",
            color=discord.Color.red()
        )
        embed.add_field(name="Staff", value=target.mention)
        embed.add_field(name="Actions", value=str(actions))

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ModStats(bot))
