import discord
from discord.ext import commands
from discord import app_commands

class bot_clear(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name = "bot_clear", description = "Delete all messages sent by the bot in this DM")
    @app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
    @app_commands.user_install()
    async def clear_bot_messages(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral = True)

        async for message in interaction.channel.history(limit = 1000):
            if message.author.id == self.bot.user.id:
                try:
                    await message.delete()
                except:
                    pass
        
        await interaction.followup.send(embed = discord.Embed(description = f"🧹 ‎ Cleared `{self.bot.user}`'s messages."), ephemeral = True)

async def setup(bot):
    await bot.add_cog(bot_clear(bot))