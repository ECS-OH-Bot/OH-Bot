import discord
from discord.ext import commands

class OH_Queue(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._OHQueue = list()

    @commands.command(aliases=["listqueue", "lsq"])
    async def listQueue(self, ctx):
        """
        List all users in the queue
        @ctx: context object containing information about the caller (this will be passed in by the discord API)
        """
        msg = ''
        count = 1
        for user in self._OHQueue:
            name = f"{count}: {user.name}\n"
            msg += name
            count += 1
        if len(self._OHQueue):
            await ctx.send(f"Current users in queue:\n {msg}")
        else:
            await ctx.send("Queue is currently empty ")

    @commands.command(aliases=["enterqueue", "eq"])
    async def enterQueue(self, ctx: discord.ext.commands.context.Context):
        """
        Enters user into the OH queue
        if they already are enqueued return them their position in queue
        @ctx: context object containing information about the caller
        """
        sender = ctx.author._user
        if sender not in self._OHQueue:
            self._OHQueue.append(sender)
            position = self._OHQueue.index(sender) + 1
            await ctx.send(
                f"{sender.mention} you have been added to the queue\n"
                f"Current Position: {position}"
            )
        else:
            position = self._OHQueue.index(sender) + 1
            await ctx.send(
                f"{sender.mention} you are already in the queue. Please wait to be called\n"
                f"Current position: {position}"
            )
        # Call the list queue function to let them know where they stand in the queue
        await self.listQueue(ctx)

    @commands.command(aliases=['leavequeue', 'lq'])
    async def leaveQueue(self, ctx):
        """
        Removes caller from the queue
        @ctx: context object containing information about the caller
        """
        sender = ctx.author._user
        if sender in self._OHQueue:
            self._OHQueue.remove(sender)
            await ctx.send(f"{sender.mention} you have been removed from the queue")
        else:
            await ctx.send(f"{sender.mention} you were not in the queue")

        # Let the caller know what the queue looks like now
        await self.listQueue(ctx)

    @commands.command()
    async def dequeueStudent(self, ctx):
        """
        Dequeue a student from the queue and notify them
        @ctx: context object containing information about the caller
        """
        sender = ctx.author._user



def setup(client):
    """
    Called internally by discord API cog functionality
    I honestly have no idea how this works...
    """
    client.add_cog(OH_Queue(client))