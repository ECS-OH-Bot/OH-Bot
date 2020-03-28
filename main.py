import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DISCORD_GUILD = os.getenv("DISCORD_GUILD")
QUEUE_CHANNEL_ID = os.getenv("QUEUE_CHANNEL_ID")
WAITING_ROOM_CHANNEL_ID = os.getenv("WAITING_ROOM_CHANNEL_ID")

client = commands.Bot(command_prefix=">")

if __name__ == '__main__':
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")
    client.run(BOT_TOKEN)