import os
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
QUEUE_CHANNEL_ID = os.getenv("QUEUE_CHANNEL_ID")
ADMIN = os.getenv("ADMIN")
STUDENT = os.getenv("STUDENT")
INSTRUCTOR_ROLE_ID = int(os.getenv("INSTRUCTOR_ROLE_ID"))
STUDENT_ROLE_ID = (os.getenv("STUDENT_ROLE_ID"))

client = commands.Bot(command_prefix=">")
client.remove_command("help")

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