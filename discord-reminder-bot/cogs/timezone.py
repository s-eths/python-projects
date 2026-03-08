import discord, json, os
from discord.ext import commands
from discord import app_commands

def load_data():
    if not os.path.exists("data/reminders.json"):
        return {}
    with open("data/reminders.json", "r") as data:
        return json.load(data)

class timezone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "timezone", description = "View your currently set timezone")
    async def timezone(self, interaction: discord.Interaction):
        data = load_data()

        if str(interaction.user.id) not in data or "timezone" not in data[str(interaction.user.id)]:
            await interaction.response.send_message(embed = discord.Embed(description = f"❌ ‎ You haven't set a timezone yet.\n\nUse `/timezone_set` first."), ephemeral = True)
            return

        await interaction.response.send_message(embed = discord.Embed(description = f"🌍 ‎ Your timezone is **{data[str(interaction.user.id)]['timezone']}**"), ephemeral = True)

async def setup(bot):
    await bot.add_cog(timezone(bot))