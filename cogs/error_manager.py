"""
Cog to facilitate the handling of errors raised by bot commands across all cogs
"""

from logging import getLogger

from discord import Permissions
from discord.ext import commands
from discord.ext.commands import Bot, Context

from constants import GetConstants
from errors import CommandPermissionError, OHStateError

logger = getLogger(f"main.{__name__}")



class ErrorManager(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, context: Context, err: Exception) -> None:
        """
        Handle errors raised by commands across all cogs
        """

        sender = context.author

        # The sender entered a command we do not recognize
        if isinstance(err, commands.CommandNotFound):
            await context.send(
                f"Command '{context.invoked_with}' does not exist\n"
                f"Check your spelling."
            )
            logger.warning(f"{context.author} attempted to use the invalid command {context.invoked_with}")
        # Non-admin tried to use an admin command
        elif isinstance(err, CommandPermissionError):
            await context.author.send(
                f"You do not have permission to use {context.invoked_with}\n"
                f"If you think this is a mistake DM the Admin: Grant Gilson."
            )
            logger.warning(f"{context.author} tried to use {context.invoked_with}"
                           f" for which they have no permssions")
        # Someone tried to open/close OH but they were already open/closed
        elif isinstance(err, OHStateError):
            await context.author.send("I could not complete the command. "
                                      f"{err}")
            logger.warning(f"{context.author} attempted to open/close office hours"
                           f"when they were already closed/open")
        # There was some other error: probably an internal error
        elif isinstance(err, Exception):
            await sender.send("I have encountered an internal error in processing your last command. "
                              "If the error persists please contact Grant Gilson."
                              )
            logger.critical("An internal error has occured during processing of a command\n"
                             f"\tCommand: {context.invoked_with}"
                             f"\tSender: {context.author}"
                             f"\tChannel: {context.channel}",
                             exc_info=err, stack_info=True
                             )

        # Once the error has been handled, delete the offending message if we have permission to do so
        if context.channel.permissions_for is not None:
            permissions: Permissions = context.channel.permissions_for(context.me)
            if permissions.manage_messages:
                await context.message.delete()


def setup(bot: Bot) -> None:
    bot.add_cog(ErrorManager(bot))
