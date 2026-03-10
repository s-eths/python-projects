import discord, json, os, re, datetime
from discord.ext import commands
from discord import app_commands
from datetime import timezone, timedelta

def load_data():
    if not os.path.exists("data/reminders.json"):
        return {}
    with open("data/reminders.json", "r") as data:
        return json.load(data)

def save_data(data):
    os.makedirs("data", exist_ok = True)
    with open("data/reminders.json", "w") as f:
        json.dump(data, f, indent = 4)

def parse_utc_offset(tz_input: str):
    tz_input = tz_input.strip().upper()

    match = re.match(r"UTC([+-])(\d{1,2})(?::?(\d{2}))?$", tz_input)
    if not match:
        return None
    return timezone((1 if match.group(1) == "+" else -1) * timedelta(hours = int(match.group(2)), minutes = int(match.group(3) or 0)))

class timezone_set(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "timezone_set", description = "Set your timezone (Example: UTC+11, UTC-5, UTC+10:30)")
    @app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
    @app_commands.user_install()
    async def timezone_set(self, interaction: discord.Interaction, utc_offset: str):
        if parse_utc_offset(utc_offset) is None:
            await interaction.response.send_message(embed = discord.Embed(description = f"❌ ‎ Invalid timezone format.\n\nExamples: `UTC+11`, `UTC-5`, `UTC+10:30`"), ephemeral = True)
            return

        data = load_data()

        if str(interaction.user.id) not in data:
            data[str(interaction.user.id)] = {"timezone": utc_offset.upper(), "reminders": []}
        else:
            data[str(interaction.user.id)]["timezone"] = utc_offset.upper()

        save_data(data)
        await interaction.response.send_message(embed = discord.Embed(description = f"🌍 ‎ Timezone set to **{utc_offset.upper()}**"), ephemeral = True)

async def setup(bot):
    await bot.add_cog(timezone_set(bot))