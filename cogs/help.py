import asyncio

import yaml
from discord.ext import commands
from discord.ext.commands import Context
from yaml import load, add_constructor

from user_utils import isAdmin
from cogs.tools import selfClean


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

        def join(loader, node):
            seq = loader.construct_sequence(node)
            return ''.join([str(i) for i in seq])

        add_constructor('!join', join)

        with open('help_messages.yaml', 'r') as file:
            self.help_messages = load(file, Loader=yaml.Loader)

    @commands.group(name='help', invoke_without_command=True)
    async def help_cmd(self, ctx: Context) -> None:
        help_string = self.help_messages['all_admin'] if await isAdmin(ctx) \
            else self.help_messages['all_student']

        await asyncio.gather(ctx.author.send(help_string), selfClean(ctx))

    @help_cmd.command(name='queue')
    async def queue_help(self, ctx: Context) -> None:
        help_string = self.help_messages['queue_admin'] if await isAdmin(ctx) \
            else self.help_messages['queue_student']

        await asyncio.gather(ctx.author.send(help_string), selfClean(ctx))

    @help_cmd.command(name='voice')
    async def voice_help(self, ctx: Context) -> None:
        help_string = self.help_messages['voice_help']
        await ctx.author.send(help_string)
        await selfClean(ctx)


def setup(client):
    client.add_cog(Help(client))