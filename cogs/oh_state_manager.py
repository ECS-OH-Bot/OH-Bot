"""
Cog to manage opening / closing office hours
"""
from discord.ext.commands import Cog, Bot, Context
from discord.ext import commands

from enum import Enum

from user_utils import isAdmin
from errors import OHStateError

class OHState(Enum):
    CLOSED = 0
    OPEN = 1


async def officeHoursAreClosed(context: Context) -> bool:
    if not context.bot.get_cog("OHStateManager").state == OHState.CLOSED:
        raise OHStateError("Office hours are not closed.")
    return True

async def officeHoursAreOpen(context: Context) -> bool:
    if not context.bot.get_cog("OHStateManager").state == OHState.OPEN:
        raise OHStateError("Office hours are not open.")
    return True

class OHStateManager(Cog):
    def __init__(self):
        self.state: OHState = OHState.CLOSED

    @commands.command(aliases=["open", "start"])
    @commands.check(officeHoursAreClosed)
    @commands.check(isAdmin)
    async def startOH(self, context: Context):
        await context.author.send("Office hours have been opened. Students may now queue up")
        self.state = OHState.OPEN
        # Trigger the queue message to reprint
        await context.bot.get_cog("OH_Queue").onQueueUpdate()

    @commands.command(aliases=["close", "end"])
    @commands.check(officeHoursAreOpen)
    async def stopOH(self, context: Context):
        await context.author.send("Office hours have been closed. No new students will be added to the queue.")
        self.state = OHState.CLOSED
        # Trigger the queue message to reprint
        await context.bot.get_cog("OH_Queue").onQueueUpdate()

def setup(bot: Bot):
    bot.add_cog(OHStateManager())