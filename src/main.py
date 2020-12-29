from logging import getLogger
import os
from asyncio import gather
from discord.ext import commands
from discord import Intents
from discord.utils import get
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

    # As of version >1.5.0 of the discord py API intents need to be configured. 
    intents = Intents.default()
    # The bot intends to manage users. I.e. detect when the join and assign roles.
    intents.members = True

    # Create the discord.py bot
    bot: commands.Bot = commands.Bot(command_prefix=GetConstants().COMMAND_CHAR, intents=intents)
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

    # Automatically assign new members to the "student" role
    @bot.event
    async def on_member_join(member):
        """
        On new student joining guild assign them student role and send them a welcome message
        """
        print("on join")
        role = get(member.guild.roles, name=GetConstants().STUDENT)
        await gather(member.add_roles(role),
                     member.send(f"{member.mention} welcome! You have been promoted to the role of Student"),
                     member.send(bot.get_cog("Help").help_messages['all_student'])
                     )
        logger.debug(f"{member.mention} has joined the server")

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
    os.chdir("src")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            logger.debug(f"Loading in the cog {filename}")
            bot.load_extension(f"cogs.{filename[:-3]}")


if __name__ == '__main__':
    main()
