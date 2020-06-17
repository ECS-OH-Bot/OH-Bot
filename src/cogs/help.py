import asyncio
from logging import getLogger

import yaml
from discord.ext import commands
from discord.ext.commands import Context
from yaml import load, add_constructor

from user_utils import isAdmin
from cogs.tools import selfClean
from constants import GetConstants
from errors import CommandPermissionError

logger = getLogger(f"main.{__name__}")


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

        def join(loader, node):
            seq = loader.construct_sequence(node)
            return ''.join([str(i) for i in seq])

        add_constructor('!join', join)

        with open(GetConstants().HELP_MESSAGES, 'r') as file:
            self.help_messages = load(file, Loader=yaml.Loader)

    @commands.group(name='help', invoke_without_command=True)
    async def help_cmd(self, ctx: Context) -> None:
        try:
            await isAdmin(ctx)
            logger.debug(f"{ctx.author} requested to see all admin commands")
            help_string = self.help_messages['all_admin']
        except CommandPermissionError:
            logger.debug(f"{ctx.author} requested to see all student commands")
            help_string = self.help_messages['all_student']

        await asyncio.gather(ctx.author.send(help_string), selfClean(ctx))

    @help_cmd.command(name='queue')
    async def queue_help(self, ctx: Context) -> None:
        try:
            await isAdmin(ctx)
            logger.debug(f"{ctx.author} requested to see admin commands for the queue")
            help_string = self.help_messages['queue_admin']
        except CommandPermissionError:
            logger.debug(f"{ctx.author} requested to see student commands for the queue")
            help_string = self.help_messages['queue_student']

        await asyncio.gather(ctx.author.send(help_string), selfClean(ctx))

    @help_cmd.command(name='voice')
    async def voice_help(self, ctx: Context) -> None:
        logger.debug(f"{ctx.author} requested to see voice commands")
        help_string = self.help_messages['voice_help']
        await asyncio.gather(ctx.author.send(help_string), selfClean(ctx))

    @commands.command(aliases=["refreshhelp"])
    @commands.check(isAdmin)
    async def refresh_help(self, ctx: Context) -> None:
        help_string = self.help_messages['all_student']
        await ctx.channel.purge()
        await ctx.channel.send(help_string)

        logger.debug(f"{ctx.author} has refreshed the help page")


def setup(client):
    client.add_cog(Help(client))
