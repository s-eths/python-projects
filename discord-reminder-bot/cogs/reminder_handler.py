import discord, json, os, re
from discord.ext import commands, tasks
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

class reminder_handler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_reminders.start()

    @tasks.loop(seconds = 5)
    async def check_reminders(self):
        data = load_data()
        now_utc = datetime.utcnow()
        updated = False

        for user_id, info in data.items():
            reminders_list = info.get("reminders", [])
            time_zone_offset = parse_utc_offset(info.get("timezone", "UTC+0"))

            for reminder in reminders_list[:]:
                remind_time_local = datetime.strptime(reminder["time"], "%Y-%m-%d %H:%M:%S")
                remind_time_utc = remind_time_local - time_zone_offset

                if now_utc >= remind_time_utc:
                    try:
                        user = await self.bot.fetch_user(int(user_id))

                        if reminder.get("type") == "recurring":
                            await user.send(content = user.mention, embed = discord.Embed(title = "Reminder", description = f"⏰ ‎ {reminder['text']}\n`{remind_time_local.strftime('%d-%m-%Y %I:%M %p')}`"))
                            delta = parse_interval(reminder.get("interval"))
                            if delta:
                                reminder["time"] = (remind_time_local + delta).strftime("%Y-%m-%d %H:%M:%S")
                                updated = True
                        else:
                            await user.send(content = user.mention, embed = discord.Embed(title = "Reminder", description = f"⏰ ‎ {reminder['text']}\n`{remind_time_local.strftime('%d-%m-%Y %I:%M %p')}`"))
                            reminders_list.remove(reminder)
                            updated = True
                    except Exception as error:
                        print(f"Failed to send reminder to {user_id}: {error}")

        if updated:
            save_data(data)

    @check_reminders.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(reminder_handler(bot))