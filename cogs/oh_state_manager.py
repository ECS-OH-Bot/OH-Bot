"""
Cog to manage opening / closing office hours
"""
from discord.ext.commands import Cog, Bot, Context
from discord.ext import commands

from cogs.user_utils import UserUtils

from enum import Enum
class OHState(Enum):
    CLOSED = 0
    OPEN = 1

class OHStateManager(Cog):
    state = OHState.CLOSED

    def __init__(self, bot: Bot):
        self.bot = Bot

    @classmethod
    def officeHoursAreClosed(cls) -> bool:
        return OHStateManager.state == OHState.CLOSED

    @classmethod
    def officeHoursAreOpen(cls) -> bool:
        return OHStateManager.state == OHState.OPEN

    @commands.command(aliases=["open", "start"])
    #@commands.check(officeHoursAreClosed)
    @commands.check(UserUtils.isAdmin)
    async def startOH(self, context: Context):
        await context.author.send("Office hours have been opened. Students may now queue up")
        self.state = OHState.OPEN

    @commands.command(aliases=["close", "end"])
    @commands.check(officeHoursAreOpen)
    @commands.check(UserUtils.isAdmin)
    async def stopOH(self, context: Context):
        await context.author.send("Office hours have been closed. No new students will be added to the queue.")
        self.state = OHState.OPEN

def setup(bot: Bot):
    bot.add_cog(OHStateManager(bot))