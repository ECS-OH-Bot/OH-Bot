from typing import Optional
from discord import Client, TextChannel, VoiceChannel, Invite, User, Permissions
from discord.ext import commands
from discord.ext.commands.context import Context
from .roleManager import isAdmin, getSender, getGuildMemberFromUser
from main import QUEUE_CHANNEL_ID, WAITING_ROOM_CHANNEL_ID, DISCORD_GUILD


class OH_Queue(commands.Cog):

    def __init__(self, client : Client):
        self.client = client
        self.OHQueue = list()
        self.admins = list()
        # Channel references are resolved by the pre invoke hook
        self.queue_channel: Optional[TextChannel] = None
        self.waiting_room: Optional[VoiceChannel] = None

    async def cog_before_invoke(self, context: Context) -> None:
        if self.queue_channel is None:
            self.queue_channel = await self.client.fetch_channel(QUEUE_CHANNEL_ID)
        if self.waiting_room is None:
            self.waiting_room = await self.client.fetch_channel(WAITING_ROOM_CHANNEL_ID)

    async def cog_after_invoke(self, context: Context) -> None:
        await self.onQueueUpdate()

        # Delete the command message if we have permission to do so
        if context.channel.permissions_for is not None:
            permissions: Permissions = context.channel.permissions_for(context.me)
            if permissions.manage_messages:
                await context.message.delete()

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

        sender = getSender(context)
        if sender not in self.OHQueue:
            self.OHQueue.append(sender)
            position = len(self.OHQueue)

            # Respond to user
            await sender.send(
                f"{sender.mention} you have been added to the queue\n"
                f"Current Position: {position}"
            )

            # Move the user into the waiting room if we can
            if isinstance(sender, User) or sender.voice is None:
                # If the command comes from DMs or the user is not connected to voice, instruct them to join
                invite: Invite = await self.waiting_room.create_invite()
                await sender.send("Please join the waiting room until you are called on. **If you leave the waiting room \
you will be removed from the queue.**")
                await sender.send(invite.url)
            else:
                await sender.move_to(self.waiting_room)
                await sender.send("I have moved you into the waiting room. **If you leave the waiting room you will be \
removed from the queue.**")

        else:
            position = self.OHQueue.index(sender) + 1
            await sender.send(
                f"{sender.mention} you are already in the queue. Please wait to be called\n"
                f"Current position: {position}"
            )


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
            # Remove this student from the voice channels
            await sender.move_to(None)
        else:
            await sender.send(f"{sender.mention} you were not in the queue")



    @commands.command(aliases=["dequeue", 'dq'])
    @commands.check(isAdmin)
    async def dequeueStudent(self, context: Context):
        """
        Dequeue a student from the queue and notify them
        @ctx: context object containing information about the caller
        """
        if len(self.OHQueue):
            sender = getSender(context)
            student = self.OHQueue.pop(0)
            await student.send(f"Summoning {student.mention} to {sender.mention} OH")


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


def setup(client):
    """
    This python file is an 'extension'. The setup file acts as the entry point to the extension.
    In our setup we load the cog we have written to be used in the discord bot
    """
    client.add_cog(OH_Queue(client))