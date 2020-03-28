import os
from discord.ext import commands
from constants import Constants, GetConstants

def main():
    # Instantiate constants singleton
    Constants()

    # Create the discord.py bot
    bot: commands.Bot = commands.Bot(command_prefix="/")
    before_cog_load(bot)
    load_cogs(bot)
    after_cog_load(bot)

    # Start the bot
    bot.run(GetConstants().BOT_TOKEN)

def before_cog_load(bot: commands.Bot) -> None:
    """
    Called immediately before cogs are loaded and the client is run
    :param bot: The instance of the bot
    """
    bot.remove_command("help")

def after_cog_load(bot: commands.Bot) -> None:
    """
    Called immediately after cogs are loaded and the client is run
    :param bot: The instance of the bot
    """
    pass

def load_cogs(bot: commands.Bot) -> None:
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")

if __name__ == '__main__':
    main()