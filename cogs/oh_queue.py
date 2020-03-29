from typing import Optional, List

from discord import Client, TextChannel, VoiceChannel, Invite, User, Permissions, Member
from discord.ext import commands
from discord.ext.commands.context import Context

from cogs.tools import selfClean
from cogs.user_utils import UserUtils

from constants import GetConstants

class OH_Queue(commands.Cog):

    def __init__(self, client: Client):
        self.client = client
        self.OHQueue: List[Member] = list()
        self.admins = list()
        # Channel references are resolved by the pre invoke hook
        self.queue_channel: Optional[TextChannel] = None
        self.waiting_room: Optional[VoiceChannel] = None

    async def cog_before_invoke(self, context: Context) -> None:
        if self.queue_channel is None:
            self.queue_channel = await self.client.fetch_channel(GetConstants().QUEUE_CHANNEL_ID)
        if self.waiting_room is None:
            self.waiting_room = await self.client.fetch_channel(GetConstants().WAITING_ROOM_CHANNEL_ID)

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

        sender = context.author
        if sender not in self.OHQueue:
            # Append the Member instance to the queue.
            if isinstance(sender, User):
                self.OHQueue.append(await UserUtils.userToMember(sender))
            else:
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
                await sender.send("Please join the waiting room until you are called on. **If you are not in the \
waiting room or breakout rooms when you are called on, you will be removed from the queue!**")
                await sender.send(invite.url)
            else:
                await sender.move_to(self.waiting_room)
                await sender.send("I have moved you into the waiting room. **If you are not in the waiting room or \
breakout rooms when you are called on, you will be removed from the queue!**")

        else:
            position = self.OHQueue.index(sender) + 1
            await sender.send(
                f"{sender.mention} you are already in the queue. Please wait to be called\n"
                f"Current position: {position}"
            )
        await selfClean(context)


    @commands.command(aliases=['leavequeue', 'lq'])
    async def leaveQueue(self, context: Context):
        """
        Removes caller from the queue
        @ctx: context object containing information about the caller
        """

        sender = context.author
        if sender in self.OHQueue:
            self.OHQueue.remove(sender)
            await sender.send(f"{sender.mention} you have been removed from the queue")
        else:
            await sender.send(f"{sender.mention} you were not in the queue")
        await selfClean(context)


    @commands.command(aliases=["dequeue", 'dq'])
    @commands.check(UserUtils.isAdmin)
    async def dequeueStudent(self, context: Context):
        """
        Dequeue a student from the queue and notify them
        @ctx: context object containing information about the caller
        """
        sender = context.author
        if isinstance(sender, User):
            # If the command was sent via DM, tell them to do it from the bot channel instead
            await sender.send("Due to technical limitations, you must send the dequeue command from the bot commands \
channel")
            return

        if sender.voice is None:
            await sender.send("You must be connected to a voice channel to do this. The queue has not been modified.")

        elif len(self.OHQueue):
            student = self.OHQueue.pop(0)
            if student.voice is None:
                await sender.send(f"{student.mention} is not in the waiting room or any of the breakout rooms. I cannot\
 move them into your voice channel. They have been removed from the queue.")
            else:
                await student.send(f"You are being summoned to {sender.mention}'s OH")
                # Add this student to the voice chat
                await student.move_to(sender.voice.channel)
        else:
            await sender.send("The queue is empty. Perhaps now is a good time for a coffee break?")

    @commands.command(aliases=["cq", "clearqueue"])
    @commands.check(UserUtils.isAdmin)
    async def clearQueue(self, context: Context):
        """
        Clears all students from the queue
        @ctx: context object containing information about the caller
        """
        sender = context.author
        self.OHQueue.clear()
        await sender.send(f"{sender.mention} has cleared the queue")
        await selfClean(context)


def setup(client):
    """
    This python file is an 'extension'. The setup file acts as the entry point to the extension.
    In our setup we load the cog we have written to be used in the discord bot
    """
    client.add_cog(OH_Queue(client))