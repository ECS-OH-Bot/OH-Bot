import discord
import os
import logging
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

client = commands.Bot(command_prefix=">")

@client.command
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")

@client.command
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")

if __name__ == '__main__':
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")
    client.run(BOT_TOKEN)

