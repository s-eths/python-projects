import discord, json
from discord.ext import commands
import os

with open("data/config.json", "r") as data:
    data = json.load(data)

bot = commands.Bot(command_prefix = ",", intents = discord.Intents.all())

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
    except Exception as error:
        print(error)

async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(data["token"])

import asyncio
asyncio.run(main())