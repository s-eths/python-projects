import discord, json, os
from discord.ext import commands
from discord import app_commands

def load_data():
    if not os.path.exists("data/reminders.json"):
        return {}
    with open("data/reminders.json", "r") as data:
        return json.load(data)

def save_data(data):
    os.makedirs("data", exist_ok = True)
    with open("data/reminders.json", "w") as _data:
        json.dump(data, _data, indent = 4)

class remove_reminder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name = "remove_reminder", description = "Remove a reminder by its ID")
    @app_commands.describe(reminder_id = "The ID of the reminder you want to remove")
    async def remove_reminder(self, interaction: discord.Interaction, reminder_id: str):
        await interaction.response.defer(ephemeral = True)
        data = load_data()

        if str(interaction.user.id) not in data or not data[str(interaction.user.id)].get("reminders"):
            await interaction.followup.send(embed = discord.Embed(description = f"❌ ‎ You have no reminders set."), ephemeral = True)
            return

        reminders = data[str(interaction.user.id)]["reminders"]
        for reminder in reminders:
            if reminder.get("id") == reminder_id:
                reminders.remove(reminder)
                save_data(data)
                await interaction.followup.send(embed = discord.Embed(description = f"✅ ‎ Reminder `{reminder_id}` has been removed."), ephemeral = True)
                return
        
        await interaction.followup.send(embed = discord.Embed(description = f"❌ ‎ No reminder found with ID `{reminder_id}`"), ephemeral = True)

async def setup(bot):
    await bot.add_cog(remove_reminder(bot))