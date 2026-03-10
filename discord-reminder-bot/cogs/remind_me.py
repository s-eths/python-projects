import discord, json, os, re, random
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

def load_data():
    if not os.path.exists("data/reminders.json"):
        return {}
    with open("data/reminders.json", "r") as data:
        return json.load(data)

def save_data(data):
    os.makedirs("data", exist_ok = True)
    with open("data/reminders.json", "w") as _data:
        json.dump(data, _data, indent = 4)

def parse_duration(duration_str: str):
    match = re.match(r"(\d+)([smh])$", duration_str.lower())
    if not match:
        return None
    value, unit = match.groups()
    if unit == "s": return timedelta(seconds = int(value))
    if unit == "m": return timedelta(minutes = int(value))
    if unit == "h": return timedelta(hours = int(value))
    return None

def generate_id(length = 6):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k = length))

def parse_utc_offset(time_zone: str):
    match = re.match(r"UTC([+-])(\d{1,2})(?::?(\d{2}))?$", time_zone.strip().upper())
    if not match:
        return timedelta(0)
    return timedelta(hours = int(match.group(2)) * (1 if match.group(1) == "+" else -1), minutes = int(match.group(3) or 0) * (1 if match.group(1) == "+" else -1))

class remind_me(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name = "remind_me", description = "Set a reminder")
    @app_commands.describe(duration = "Time until reminder (e.g., 30m, 2h)", message = "What to remind you about.")
    @app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
    @app_commands.user_install()
    async def remind_me(self, interaction: discord.Interaction, duration: str, message: str):
        await interaction.response.defer(ephemeral = True)

        if not parse_duration(duration):
            await interaction.followup.send(embed = discord.Embed(description = f"❌ ‎ Invalid duration format.\nExamples: `30m`, `2h`, `45s`"), ephemeral = True)

        data = load_data()

        if str(interaction.user.id) not in data:
            data[str(interaction.user.id)] = {"timezone": "UTC+0", "reminders": []}
        elif "reminders" not in data[str(interaction.user.id)]:
            data[str(interaction.user.id)]["reminders"] = []

        time_zone_offset = parse_utc_offset(data[str(interaction.user.id)]["timezone"])
        remind_time_local = datetime.utcnow() + parse_duration(duration) + time_zone_offset
        remind_time_string = remind_time_local.strftime("%Y-%m-%d %H:%M:%S")

        existing_ids = {r["id"] for r in data[str(interaction.user.id)]["reminders"]}
        reminder_id = generate_id()
        while reminder_id in existing_ids:
            reminder_id = generate_id()

        data[str(interaction.user.id)]["reminders"].append({"id": reminder_id, "type": "one-time", "time": remind_time_string, "text": message})
        save_data(data)

        await interaction.followup.send(embed = discord.Embed(title = "Reminder Set", description = f"Message: `{message}`\n`{remind_time_string} ({data[str(interaction.user.id)]['timezone']})`"), ephemeral = True)

async def setup(bot):
    await bot.add_cog(remind_me(bot))