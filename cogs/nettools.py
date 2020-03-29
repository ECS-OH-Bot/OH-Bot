from logging import getLogger

from discord import Client
from discord.ext import commands
from discord.ext.commands import Context
from cogs.roleManager import getSender

logger = getLogger(__name__)


class NetTools(commands.Cog):

    def __init__(self, client: Client):
        self.client = client

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        logger.debug("OH Bot connected")

    @commands.Cog.listener()
    async def on_command_error(self, context: Context, err: Exception):
        """
        Error event handler
        Currently handling for err is None
        @ctx: context object containing information about the caller
        @err: error object raised by caller
        Error types currently handled:
        CommandNotFound,
        CheckFailure
        """

        sender = getSender(context)

        if isinstance(err, commands.CommandNotFound):
            logger.error(f"{sender.mention} tried to use the {context.invoked_with} command, which does not exist")
            await context.send(
                f"Command '{context.invoked_with}' does not exist\n"
                f"{sender.mention} check your spelling"
            )

        if isinstance(err, commands.CheckFailure):
            logger.error(f"{sender.mention} tried to use the {context.invoked_with} command, for which they do not "
                         f"have permssion to")
            await sender.send(
                f"{sender.mention} does not have permission to use {context.invoked_with}\n"
                f"If you think this is a mistake DM the Admin: Grant Gilson"
            )
            await context.message.delete()
        if isinstance(err, Exception):
            logger.error(err)

    #Commands
    @commands.command()
    async def ping(self, context: Context):
        logger.debug(f"ping called by {getSender(context)}")
        await context.send(f"Pong! {round(self.client.latency * 1000)}")


def setup(client):
    """
    This python file is an 'extension'. The setup file acts as the entry point to the extension.
    In our setup we load the cog we have written to be used in the discord bot
    """
    client.add_cog(NetTools(client))