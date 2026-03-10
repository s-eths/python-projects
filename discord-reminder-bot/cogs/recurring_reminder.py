import discord, json, os, re, random, string
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

def generate_id(length = 6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k = length))

def parse_datetime_user(input_str: str):
    for pattern in ["%d-%m-%Y %I:%M%p", "%d-%m-%Y %I:%M %p"]:
        try:
            return datetime.strptime(input_str.strip().upper().replace("  ", " "), pattern)
        except ValueError:
            continue
    return None

def parse_interval(interval_str: str):
    match = re.match(r"(\d+)([smhdw])$", interval_str.lower())
    if not match:
        return None
    value, unit = match.groups()
    if unit == "s": return timedelta(seconds = int(value))
    if unit == "m": return timedelta(minutes = int(value))
    if unit == "h": return timedelta(hours = int(value))
    if unit == "d": return timedelta(days = int(value))
    if unit == "w": return timedelta(weeks = int(value))
    return None

class recurring_reminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name = "recurring_reminder", description = "Set a recurring reminder at a specific date/time with an interval")
    @app_commands.describe(datetime_str = "Date and time (DD-MM-YYYY HH:MM AM/PM)", interval = "Recurring interval (e.g., 1d, 2h, 30m)", message = "What to remind you about")
    @app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
    @app_commands.user_install()
    async def recurring_reminder(self, interaction: discord.Interaction, datetime_str: str, interval: str, message: str):
        await interaction.response.defer(ephemeral = True)

        data = load_data()

        if str(interaction.user.id) not in data:
            data[str(interaction.user.id)] = {"timezone": "UTC+0", "reminders": []}
        elif "reminders" not in data[str(interaction.user.id)]:
            data[str(interaction.user.id)]["reminders"] = []

        start_time = parse_datetime_user(datetime_str)
        if not start_time:
            await interaction.followup.send(embed = discord.Embed(description = f"❌ ‎ Invalid date/time format.\nUse: `DD-MM-YYYY HH:MM AM/PM`"), ephemeral = True)

        delta = parse_interval(interval)
        if not delta:
            await interaction.followup.send(embed = discord.Embed(description = f"❌ ‎ Invalid duration format.\nExamples: `1d`, `2h`, `30m`, `1w`"), ephemeral = True)
            return

        existing_ids = {r["id"] for r in data[str(interaction.user.id)]["reminders"]}
        reminder_id = generate_id()
        while reminder_id in existing_ids:
            reminder_id = generate_id()

        data[str(interaction.user.id)]["reminders"].append({"id": reminder_id, "type": "recurring", "time": start_time.strftime("%Y-%m-%d %H:%M:%S"), "interval": interval, "text": message})
        save_data(data)

        await interaction.followup.send(embed = discord.Embed(title = "Reminder Set", description = f"Message: `{message}`\n`{start_time.strftime('%d-%m-%Y %I:%M %p')} ({data[str(interaction.user.id)]['timezone']})`"), ephemeral = True)

async def setup(bot):
    await bot.add_cog(recurring_reminder(bot))