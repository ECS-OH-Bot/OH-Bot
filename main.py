import os
from discord.ext import commands
from constants import Constants, GetConstants

# Argparse configuration
import argparse
parser = argparse.ArgumentParser(description="Enable debugging output")
parser.add_argument('--debug', action='store_true')

def main():
    # Instantiate constants singleton
    # For convenience, this object holds onto command line arguments
    Constants(parser.parse_args())

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

    # Remove the default help command so that we may implement a more sophisticated one
    bot.remove_command("help")

    # When the bot is ready, print a message to the terminal.
    async def on_ready(): print("The bot is online! Happy helping.")
    bot.add_listener(on_ready)

    # Add a ping command
    # TODO: Is this needed?
    @commands.command()
    async def ping(context: commands.Context): await context.author.send(f"Pong! {round(bot.latency * 1000)}")

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