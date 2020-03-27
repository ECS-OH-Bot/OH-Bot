import os
from discord.ext import commands
from dotenv import load_dotenv

QUEUE_CHANNEL_ID=692894015565332521 # TODO: Move these to env?

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
client = commands.Bot(command_prefix=">")

# region cogLoaders
"""
This group of commands may be completely useless and will likely be deprecated later
"""
@client.command
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")

@client.command
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")

# endregion

if __name__ == '__main__':
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")
    client.run(BOT_TOKEN)