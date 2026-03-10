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

def parse_utc_offset(timezone: str):
    match = re.match(r"UTC([+-])(\d{1,2})(?::?(\d{2}))?$", timezone.strip().upper())
    if not match:
        return timedelta(0)
    return timedelta(hours = int(match.group(2)) * (1 if match.group(1) == "+" else -1), minutes = int(match.group(3) or 0) * (1 if match.group(1) == "+" else -1))

def generate_id(length = 6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k = length))

def parse_datetime_user(input_str: str):
    for pattern in ["%d-%m-%Y %I:%M%p", "%d-%m-%Y %I:%M %p"]:
        try:
            return datetime.strptime(input_str.strip().upper().replace("  ", " "), pattern)
        except ValueError:
            continue
    return None

class reminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name = "reminder", description = "Set a reminder for a specific date/time")
    @app_commands.describe(datetime_str = "Date and time (DD-MM-YYYY HH:MM AM/PM)", message = "What to remind you about")
    @app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
    @app_commands.user_install()
    async def reminder(self, interaction: discord.Interaction, datetime_str: str, message: str):
        await interaction.response.defer(ephemeral = True)

        data = load_data()

        if str(interaction.user.id) not in data:
            data[str(interaction.user.id)] = {"timezone": "UTC+0", "reminders": []}
        elif "reminders" not in data[str(interaction.user.id)]:
            data[str(interaction.user.id)]["reminders"] = []

        remind_time_local = parse_datetime_user(datetime_str)

        if not remind_time_local:
            await interaction.followup.send(embed = discord.Embed(description = f"❌ ‎ Invalid date/time format.\nUse: `DD-MM-YYYY HH:MM AM/PM`"), ephemeral = True)
            return

        remind_time_string = remind_time_local.strftime("%Y-%m-%d %H:%M:%S")
        existing_ids = {r["id"] for r in data[str(interaction.user.id)]["reminders"]}
        reminder_id = generate_id()
        while reminder_id in existing_ids:
            reminder_id = generate_id()

        data[str(interaction.user.id)]["reminders"].append({"id": reminder_id, "type": "one-time", "time": remind_time_string, "text": message})
        save_data(data)

        await interaction.followup.send(embed = discord.Embed(title = "Reminder Set", description = f"Message: `{message}`\n`{remind_time_local.strftime('%d-%m-%Y %I:%M %p')} ({data[str(interaction.user.id)]['timezone']})`"), ephemeral = True)

async def setup(bot):
    await bot.add_cog(reminder(bot))