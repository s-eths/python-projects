import discord, json, os, re
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

def load_data():
    if not os.path.exists("data/reminders.json"):
        return {}
    with open("data/reminders.json", "r") as data:
        return json.load(data)

def parse_utc_offset(timezone: str):
    match = re.match(r"UTC([+-])(\d{1,2})(?::?(\d{2}))?$", timezone.strip().upper())
    if not match:
        return timedelta(0)
    return timedelta(hours = int(match.group(2)) * (1 if match.group(1) == "+" else -1), minutes = int(match.group(3) or 0) * (1 if match.group(1) == "+" else -1))

class reminders(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name = "reminders", description = "Show all your current reminders")
    async def reminders(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral = True)
        data = load_data()

        if str(interaction.user.id) not in data or not data[str(interaction.user.id)].get("reminders"):
            await interaction.followup.send(embed = discord.Embed(description = f"❌ ‎ You have no reminders set."), ephemeral = True)
            return

        time_zone_string = data[str(interaction.user.id)].get("timezone", "UTC+0")

        embed = discord.Embed(title = "Reminders")
        reminders_list = data[str(interaction.user.id)]["reminders"]

        for idx, reminder in enumerate(reminders_list, start=1):
            type_map = {"one-time": "One-Time", "recurring": "Recurring"}
            reminder_type = type_map.get(reminder.get("type", "one-time").lower(), reminder.get("type", "one-time"))
            text = reminder.get("text", "No message")
            time_str = reminder.get("time")
            try:
                time_datetime = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                display_time = time_datetime.strftime("%d-%m-%Y %I:%M %p") + f" {time_zone_string}"
            except:
                display_time = time_str + f" {time_zone_string}"

            interval_str = ""
            if reminder_type.lower() == "recurring":
                interval_str = f"\nInterval: `{reminder.get('interval','Unknown')}`"

            embed.add_field(name = f"Reminder #{idx}", value = f"ID: `{reminder.get('id','')}`\nType: `{reminder_type}`\nMessage: `{text}`\nNext Reminder: `{display_time}`{interval_str}", inline = False)

        await interaction.followup.send(embed = embed, ephemeral = True)

async def setup(bot):
    await bot.add_cog(reminders(bot))