import discord
from discord.ext import commands
from .roleManager import isAdmin, isStudent
from main import BOT_CHANNEL_ID

class OH_Queue(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._OHQueue = list()
        self.admins = list()
        self.channel = None  # This will be populated later in execution

    # !Deprecation Warning! May be removed in future revisions
    def makeChannel(self) -> None:
        """
        Generate and populate the channel member of the cog
        This channel will be where all messages sent by the bot are outbound to
        """
        if self.channel is None:
            self.channel = self.client.get_channel(BOT_CHANNEL_ID)

    def getSender(self, ctx):
        """
        Determines caller of message
        Returns caller as a user object
        """
        return self.client.get_user(ctx.author.id)

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
        sender = self.getSender(ctx)
        if len(self._OHQueue):
            await sender.send(f"Current users in queue:\n {msg}")
        else:
            await sender.send("Queue is currently empty ")

        await ctx.message.delete()

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
            await sender.send(
                f"{sender.mention} you have been added to the queue\n"
                f"Current Position: {position}"
            )
        else:
            position = self._OHQueue.index(sender) + 1
            await sender.send(
                f"{sender.mention} you are already in the queue. Please wait to be called\n"
                f"Current position: {position}"
            )
        # Call the list queue function to let them know where they stand in the queue
        await self.listQueue(ctx)
        await ctx.message.delete()

    @commands.command(aliases=['leavequeue', 'lq'])
    async def leaveQueue(self, ctx):
        """
        Removes caller from the queue
        @ctx: context object containing information about the caller
        """
        sender = ctx.author._user
        if sender in self._OHQueue:
            self._OHQueue.remove(sender)
            await sender.send(f"{sender.mention} you have been removed from the queue")
        else:
            await sender.send(f"{sender.mention} you were not in the queue")

        # Let the caller know what the queue looks like now
        await self.listQueue(ctx)
        await ctx.message.delete()


    @commands.command(aliases=["dequeue", 'dq'])
    @commands.check(isAdmin)
    async def dequeueStudent(self, ctx):
        """
        Dequeue a student from the queue and notify them
        @ctx: context object containing information about the caller
        """
        if len(self._OHQueue):
            sender = ctx.author._user
            student = self._OHQueue.pop(0)
            await student.send(f"Summoning {student.mention} to {sender.mention} OH")

        await self.listQueue(ctx)
        await ctx.message.delete()

    @commands.command(aliases=["cq", "clearqueue"])
    @commands.check(isAdmin)
    async def clearQueue(self, ctx):
        """
        Clears all students from the queue
        @ctx: context object containing information about the caller
        """
        sender = ctx.author._user
        self._OHQueue.clear()
        await sender.send(f"{sender.mention} has cleared the queue")
        await self.listQueue(ctx)
        await ctx.message.delete()



def setup(client):
    """
    Called internally by discord API cog functionality
    I honestly have no idea how this works...
    """
    client.add_cog(OH_Queue(client))