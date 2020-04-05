"""
Cog to manage opening / closing office hours
"""
from enum import Enum
from typing import List

from discord.ext.commands import Cog, Bot, Context
from discord.ext import commands
from discord import TextChannel, Message

from user_utils import isAdmin
from errors import OHStateError
from constants import GetConstants
from cogs.tools import selfClean


class OHState(Enum):
    CLOSED = 0
    OPEN = 1


async def officeHoursAreClosed(context: Context) -> bool:
    if not context.bot.get_cog("OHStateManager").state.value == OHState.CLOSED.value:
        raise OHStateError("Office hours are not closed.")
    return True


async def officeHoursAreOpen(context: Context) -> bool:
    if not context.bot.get_cog("OHStateManager").state.value == OHState.OPEN.value:
        raise OHStateError("Office hours are not open.")
    return True


class OHStateManager(Cog):
    def __init__(self):
        self.state: OHState = OHState.CLOSED

    async def __remove_bot_messages(self, context: Context):
        """
        Remove bot messages from the announcement channel
        :return:
        """
        channel: TextChannel = await context.bot.fetch_channel(GetConstants().ANNOUNCEMENT_CHANNEL_ID)
        messages: List[Message] = await channel.history().flatten()

        filtered_message = filter(lambda message: message.author.id == context.bot.user.id, messages)
        await channel.delete_messages(filtered_message)

    @commands.command(aliases=["open", "start"])
    @commands.check(officeHoursAreClosed)
    @commands.check(isAdmin)
    async def startOH(self, context: Context):
        await context.author.send("Office hours have been opened. Students may now queue up")
        self.state = OHState.OPEN
        # Send a message to the announcements channel
        # First, delete any and all messages made by the bot to the channel
        await self.__remove_bot_messages(context)

        # Then send our announcements
        await (await context.bot.fetch_channel(
            GetConstants().ANNOUNCEMENT_CHANNEL_ID)).send("@here, the queue is now open.")

        # Trigger the queue message to reprint
        await context.bot.get_cog("OH_Queue").onQueueUpdate()
        # Remove the command message to prevent clutter
        await selfClean(context)

    @commands.command(aliases=["close", "end"])
    @commands.check(officeHoursAreOpen)
    async def stopOH(self, context: Context):
        await context.author.send("Office hours have been closed. No new students will be added to the queue.")
        self.state = OHState.CLOSED
        # Send a message to the announcements channel
        # First, delete any and all messages made by the bot to the channel
        await self.__remove_bot_messages(context)

        # Then send our announcements
        await (await context.bot.fetch_channel(
            GetConstants().ANNOUNCEMENT_CHANNEL_ID)).send("@here, the queue is now closed.")

        # Trigger the queue message to reprint
        await context.bot.get_cog("OH_Queue").onQueueUpdate()

        # Remove the command message to prevent clutter
        await selfClean(context)


def setup(bot: Bot):
    bot.add_cog(OHStateManager())
