@bot.tree.command(name="priority", description="Change ticket priority")
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.choices(level=[
    app_commands.Choice(name="Low", value="LOW"),
    app_commands.Choice(name="Medium", value="MEDIUM"),
    app_commands.Choice(name="High", value="HIGH")
])
async def priority(interaction: discord.Interaction, level: app_commands.Choice[str]):
    ...
