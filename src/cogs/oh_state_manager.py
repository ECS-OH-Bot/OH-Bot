"""
Cog to manage opening / closing office hours
"""
from asyncio import gather
from enum import Enum
from logging import getLogger
from typing import List

from discord import TextChannel, Message
from discord.ext import commands
from discord.ext.commands import Cog, Bot, Context

from constants import GetConstants
from errors import OHStateError
from user_utils import isAtLeastInstructor
from cogs.tools import selfClean

logger = getLogger(f"main.{__name__}")


class OHState(Enum):
    """
    Integer enum used to represent the two states of the queue. Either open or closed
    """
    CLOSED = 0
    OPEN = 1


async def officeHoursAreClosed(context: Context) -> bool:
    """
    Helper function that returns True if the queue is currecntly closed, and throws an exception if they are not closed
    """
    if not context.bot.get_cog("OHStateManager").state.value == OHState.CLOSED.value:
        raise OHStateError("Office hours are not closed.")
    return True


async def officeHoursAreOpen(context: Context) -> bool:
    """
    Helper function that returns True if the queue is currently open, and throws an exception if they are not open
    """
    if not context.bot.get_cog("OHStateManager").state.value == OHState.OPEN.value:
        raise OHStateError("Office hours are not open.")
    return True


class OHStateManager(Cog):
    """
    Cog that allows admins and instructors to manage when the queuue is open
    """
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
    @commands.check(isAtLeastInstructor)
    async def startOH(self, context: Context):
        """
        Opens up the queue, starting office hours
        """
        self.state = OHState.OPEN
        # Send a message to the user and delete any and all messages made by the bot to the announcements channel
        await gather(context.author.send("Office hours have been opened. Students may now queue up"),
                     self.__remove_bot_messages(context)
                     )

        if context.channel != GetConstants().QUEUE_CHANNEL_ID:
            await selfClean(context)

        # Then remove the command message, send the announcement and trigger the queue message to reprint
        await gather((await context.bot.fetch_channel(GetConstants().ANNOUNCEMENT_CHANNEL_ID)).send(
                         "@here, the queue is now open."),
                     context.bot.get_cog("OH_Queue").onQueueUpdate()
                     )
        logger.debug(f"{context.author} has opened the queue")

    @commands.command(aliases=["close", "end"])
    @commands.check(officeHoursAreOpen)
    @commands.check(isAtLeastInstructor)
    async def stopOH(self, context: Context):
        """
        Closes the queue, ending office hours
        """
        self.state = OHState.CLOSED
        # Send a message to the user and delete any and all messages made by the bot to the announcements channel
        await gather(context.author.send("Office hours have been closed. No new students will be added to the queue."),
                     self.__remove_bot_messages(context)
                     )

        if context.channel != GetConstants().QUEUE_CHANNEL_ID:
            await selfClean(context)

        # Then remove the command message, send the announcement and trigger the queue message to reprint
        await gather((await context.bot.fetch_channel(GetConstants().ANNOUNCEMENT_CHANNEL_ID)).send(
                         "@here, the queue is now closed."),
                     context.bot.get_cog("OH_Queue").onQueueUpdate()
                     )
        logger.debug(f"{context.author} has closed the queue")


def setup(bot: Bot):
    bot.add_cog(OHStateManager())
