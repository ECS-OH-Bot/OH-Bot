from typing import Optional
from discord import Client, TextChannel, Forbidden
from discord.ext import commands
from discord.ext.commands.context import Context
from .roleManager import isAdmin
from main import QUEUE_CHANNEL_ID

class OH_Queue(commands.Cog):

    def __init__(self, client : Client):
        self.client = client
        self._OHQueue = list()
        self.admins = list()
        # References to TextChannels are resolved by the pre invoke hook
        self.bot_channel: Optional[TextChannel] = None
        self.queue_channel: Optional[TextChannel] = None

    def getSender(self, context: Context):
        """
        Determines caller of message
        Returns caller as a user object
        """
        return self.client.get_user(context.author.id)

    async def cog_before_invoke(self, context: Context) -> None:
        if self.queue_channel is None:
            self.queue_channel = self.client.get_channel(QUEUE_CHANNEL_ID)

    async def cog_after_invoke(self, context: Context) -> None:
        await self.onQueueUpdate()

    async def onQueueUpdate(self) -> None:
        """
        Update the persistant queue message based on _OHQueue
        """
        message = f"There are {len(self._OHQueue)} student(s) in the queue\n"
        for (position, user) in enumerate(self._OHQueue):
            message += f"{position + 1}, {user.name}\n"

        previous_messages = await self.queue_channel.history().flatten()
        await self.queue_channel.delete_messages(previous_messages)

        await self.queue_channel.send(message)

    @commands.command(aliases=["enterqueue", "eq"])
    async def enterQueue(self, context: Context):
        """
        Enters user into the OH queue
        if they already are enqueued return them their position in queue
        @ctx: context object containing information about the caller
        """

        # TODO: Look into using context.author instead of context.author._user
        # Testing currently
        sender = self.getSender(context)
        if sender not in self._OHQueue:
            self._OHQueue.append(sender)
            position = len(self._OHQueue)

            # Respond to user
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
        await context.message.delete()


    @commands.command(aliases=['leavequeue', 'lq'])
    async def leaveQueue(self, context: Context):
        """
        Removes caller from the queue
        @ctx: context object containing information about the caller
        """

        sender = self.getSender(context)
        if sender in self._OHQueue:
            self._OHQueue.remove(sender)
            await sender.send(f"{sender.mention} you have been removed from the queue")
        else:
            await sender.send(f"{sender.mention} you were not in the queue")

        await context.message.delete()



    @commands.command(aliases=["dequeue", 'dq'])
    @commands.check(isAdmin)
    async def dequeueStudent(self, context: Context):
        """
        Dequeue a student from the queue and notify them
        @ctx: context object containing information about the caller
        """
        if len(self._OHQueue):
            sender = context.author._user
            student = self._OHQueue.pop(0)
            await student.send(f"Summoning {student.mention} to {sender.mention} OH")

        await context.message.delete()


    @commands.command(aliases=["cq", "clearqueue"])
    @commands.check(isAdmin)
    async def clearQueue(self, context: Context):
        """
        Clears all students from the queue
        @ctx: context object containing information about the caller
        """
        sender = self.getSender(context)
        self._OHQueue.clear()
        await sender.send(f"{sender.mention} has cleared the queue")
        await context.message.delete()


def setup(client):
    """
    This python file is an 'extension'. The setup file acts as the entry point to the extension.
    In our setup we load the cog we have written to be used in the discord bot
    """
    client.add_cog(OH_Queue(client))