from logging import getLogger
import os
from discord.ext import commands
from logger_util import logging_setup
from constants import Constants, GetConstants
import argparse


logger = getLogger('main')

# Argparse configuration
parser = argparse.ArgumentParser(description="Discord bot to manage office hours")
parser.add_argument('config', help='The path to the configuration file. Probably config.yaml')

def main():
    # Instantiate constants singleton
    # For convenience, this object holds onto command line arguments
    Constants(parser.parse_args())

    # Setup handlers and infrastructure for the logger
    logging_setup(logger)

    # Create the discord.py bot
    bot: commands.Bot = commands.Bot(command_prefix=GetConstants().COMMAND_CHAR)
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
    async def on_ready(): logger.debug("The bot is online! Happy helping.")
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
            logger.debug(f"Loading in the cog {filename}")
            bot.load_extension(f"cogs.{filename[:-3]}")


if __name__ == '__main__':
    main()
