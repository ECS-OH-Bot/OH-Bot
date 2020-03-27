from typing import Optional
from discord import Client, TextChannel, Forbidden
from discord.ext import commands
from discord.ext.commands.context import Context
from .roleManager import isAdmin, getSender
from main import QUEUE_CHANNEL_ID


class OH_Queue(commands.Cog):

    def __init__(self, client : Client):
        self.client = client
        self.OHQueue = list()
        self.admins = list()
        # References to TextChannels are resolved by the pre invoke hook
        self.bot_channel: Optional[TextChannel] = None
        self.queue_channel: Optional[TextChannel] = None

    async def cog_before_invoke(self, context: Context) -> None:
        if self.queue_channel is None:
            self.queue_channel = self.client.get_channel(QUEUE_CHANNEL_ID)

    async def cog_after_invoke(self, context: Context) -> None:
        await self.onQueueUpdate()

    async def onQueueUpdate(self) -> None:
        """
        Update the persistant queue message based on _OHQueue
        """
        message = f"There are {len(self.OHQueue)} student(s) in the queue\n"
        for (position, user) in enumerate(self.OHQueue):
            message += f"{position + 1}, {user.display_name}\n"

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
        # RESPONSE: Works and works better so far
        sender = getSender(context)
        if sender not in self.OHQueue:
            self.OHQueue.append(sender)
            position = len(self.OHQueue)

            # Respond to user
            await sender.send(
                f"{sender.mention} you have been added to the queue\n"
                f"Current Position: {position}"
            )

        else:
            position = self.OHQueue.index(sender) + 1
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

        sender = getSender(context)
        if sender in self.OHQueue:
            self.OHQueue.remove(sender)
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
        if len(self.OHQueue):
            sender = context.author._user
            student = self.OHQueue.pop(0)
            await student.send(f"Summoning {student.mention} to {sender.mention} OH")

        await context.message.delete()


    @commands.command(aliases=["cq", "clearqueue"])
    @commands.check(isAdmin)
    async def clearQueue(self, context: Context):
        """
        Clears all students from the queue
        @ctx: context object containing information about the caller
        """
        sender = getSender(context)
        self.OHQueue.clear()
        await sender.send(f"{sender.mention} has cleared the queue")
        await context.message.delete()


def setup(client):
    """
    This python file is an 'extension'. The setup file acts as the entry point to the extension.
    In our setup we load the cog we have written to be used in the discord bot
    """
    client.add_cog(OH_Queue(client))