import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

client = commands.Bot(command_prefix=">")

@client.event
async def on_ready():
    print(f"connected...")

if __name__ == '__main__':
    client.run(BOT_TOKEN)