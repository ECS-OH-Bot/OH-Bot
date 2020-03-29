"""
Cog to facilitate the handling of errors raised by bot commands across all cogs
"""
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord import Permissions
from constants import GetConstants

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
        # The precondition on the command failed.
        # For our purposes, the only precondition is an admin check for elevated commands.
        elif isinstance(err, commands.CheckFailure):
            await sender.send(
                f"You do not have permission to use {context.invoked_with}\n"
                f"If you think this is a mistake DM the Admin: Grant Gilson."
            )
        # There was some other error: probably an internal error
        if isinstance(err, Exception):
            await sender.send("I have encountered an internal error in processing your last command."
                              "If the error persists please contact Grant Gilson."
            )

            if GetConstants().args.debug == True:
                print("An internal error has occured during processing of a command\n"
                     f"\tCommand: {context.invoked_with}"
                     f"\tSender: {context.author}"
                     f"\tChannel: {context.channel}"
                )
            else:
                print("An internal error has occured in the processing of a command. "
                      "Run with --debug for more information"
                )

        # Once the error has been handled, delete the offending message if we have permission to do so
        if context.channel.permissions_for is not None:
            permissions: Permissions = context.channel.permissions_for(context.me)
            if permissions.manage_messages:
                await context.message.delete()

def setup(bot: Bot) -> None:
    bot.add_cog(ErrorManager(bot))