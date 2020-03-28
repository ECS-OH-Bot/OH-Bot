import os
from discord.ext import commands
from dotenv import load_dotenv

QUEUE_CHANNEL_ID=692894015565332521 # TODO: Move these to env?

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DISCORD_GUILD = os.getenv("DISCORD_GUILD")
client = commands.Bot(command_prefix=">")

if __name__ == '__main__':
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")
    client.run(BOT_TOKEN)