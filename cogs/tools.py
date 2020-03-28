from logging import getLogger

from discord.ext import commands
from discord.ext.commands import Context
from yaml import load, add_constructor

from cogs.roleManager import isAdmin, getSender

logger = getLogger(__name__)


async def selfClean(context: Context):
    """
    Deletes the message that invoked a command is possible
    """
    if context.guild is not None:
        await context.message.delete()


class Tools(commands.Cog):

    def __init__(self, client):
        self.client = client

        def join(loader, node):
            seq = loader.construct_sequence(node)
            return ''.join([str(i) for i in seq])

        add_constructor('!join', join)

        with open('help_messages.yaml', 'r') as file:
            self.help_messages = load(file, Loader=yaml.Loader)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=1):
        """
        By default this command will delete the message that calls it
        @ctx: context object containing information about the caller
        @amount
        """
        await ctx.channel.purge(limit=amount)

    @commands.command()
    async def help(self, ctx):
        help_string = self.help_messages['admin'] if await isAdmin(ctx) \
            else self.help_messages['student']
        
        await getSender(ctx).send(help_string)
        await ctx.message.delete()



def setup(client):
    """
    Called internally by discord API cog functionality
    I honestly have no idea how this works...
    """
    client.add_cog(Tools(client))