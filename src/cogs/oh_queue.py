from asyncio import gather
from collections import defaultdict
from logging import getLogger
from queue import SimpleQueue
from typing import Optional, List

from discord import TextChannel, VoiceChannel, Invite, User, Permissions, Member, Message
from discord.ext import commands
from discord.ext.commands import Bot, MemberConverter
from discord.ext.commands.context import Context
from discord.ext.commands.errors import BadArgument

from tabulate import tabulate

from user_utils import isAdmin, userToMember
from cogs.oh_state_manager import OHState, officeHoursAreOpen
from errors import CommandPermissionError, OHQueueCommandUseError

from constants import GetConstants

logger = getLogger(f"main.{__name__}")


class OH_Queue(commands.Cog):

    def __init__(self, client: Bot):
        self.client = client
        self.OHQueue: List[Member] = list()
        self.admins = list()

        self.instructor_queue: defaultdict[str, SimpleQueue] = defaultdict(SimpleQueue)

        # Channel references are resolved by the pre invoke hook
        self.queue_channel: Optional[TextChannel] = None
        self.waiting_room: Optional[VoiceChannel] = None

    async def cog_before_invoke(self, context: Context) -> None:
        if self.queue_channel is None:
            self.queue_channel = await self.client.fetch_channel(GetConstants().QUEUE_CHANNEL_ID)
            logger.debug(f"Queue channel set to :{GetConstants().QUEUE_CHANNEL_ID}")
        if self.waiting_room is None:
            self.waiting_room = await self.client.fetch_channel(GetConstants().WAITING_ROOM_CHANNEL_ID)
            logger.debug(f"Waiting room channel set to :{GetConstants().WAITING_ROOM_CHANNEL_ID}")

    async def cog_after_invoke(self, context: Context) -> None:
        # Delete the command message if we have permission to do so
        if context.channel.permissions_for is not None:
            permissions: Permissions = context.channel.permissions_for(context.me)
            if permissions.manage_messages:
                await context.message.delete()
        else:
            logger.debug("Failed to invoke OH Queue cog")

        await self.onQueueUpdate()

    async def onQueueUpdate(self) -> None:
        """
        Update the persistant queue message based on _OHQueue
        """
        # Very hacky but we need channel references to be resolved
        await self.cog_before_invoke(None)

        # Generate new queue message content
        # Get the queue status (open/closed)
        status = "**OPEN**" if self.client.get_cog("OHStateManager").state.value == OHState.OPEN.value else "**CLOSED**"
        table_data = ((position + 1, user.nick if user.nick is not None else user.name) for (position, user)
                      in enumerate(self.OHQueue))
        table_text = tabulate(table_data, ["Position", "Name"], tablefmt="fancy_grid")
        queue_text = f"The queue is currently {status}. " \
                     f"There are {len(self.OHQueue)} student(s) in the queue\n```{table_text}```"

        # Find any previous message sent by the bot in the queue channel
        previous_messages: List[Message] = await self.queue_channel.history().flatten()
        previous_queue_message: Optional[Message] = None
        for message in previous_messages:
            if message.author.id == self.client.user.id:
                previous_queue_message = message
                previous_messages.remove(previous_queue_message)
                break

        # Delete all but the found message. If there is no such message delete all messages.
        await self.queue_channel.delete_messages(previous_messages)

        # If there is an existing message, edit it. Otherwise send a new message.
        if previous_queue_message is None:
            await self.queue_channel.send(queue_text)
        else:
            await previous_queue_message.edit(content=queue_text)

        # Send the next student on the queue a courtesy message to let them know its almost their turn
        if len(self.OHQueue) > 0:
            next_student: Member = self.OHQueue[0]
            await self.OHQueue[0].send("It's almost your turn. You are number one on the queue.")
            if next_student.voice is None:
                await self.OHQueue[0].send("It looks like you are not in a voice channel right now. Make sure you join "
                                           "the waiting room before it is your turn!")

    @commands.command(aliases=["enterqueue", "eq"])
    @commands.check(officeHoursAreOpen)
    async def enterQueue(self, context: Context, student: str = None, instructor: str = None):
        """
        Enters user into the OH queue
        if they already are enqueued return them their position in queue
        @ctx: context object containing information about the caller
        """
        try:
            # Case of the normal eq use where the student enqueues themself
            if not student and not instructor:
                await self._eq_default(context)

            # Case where the two optional arguments have been passed in
            elif student and instructor and await isAdmin(context):
                await self._eq_elevated_queue(context, student, instructor)
            # Else the command was not used properly
            else:
                raise OHQueueCommandUseError

        except OHQueueCommandUseError:
            logger.error("")
            await context.author.send("You ")

    async def _eq_default(self, context: Context):
        sender = context.author
        if sender not in self.OHQueue:
            # Append the Member instance to the queue.
            if isinstance(sender, User):
                self.OHQueue.append(await userToMember(sender, context.bot))
            else:
                self.OHQueue.append(sender)
            logger.debug(f"{sender} has been added to the queue")

            position = len(self.OHQueue)

            # Respond to user
            await sender.send(
                f"You have been added to the queue\n"
                f"You are number {position} in line.", delete_after=GetConstants().MESSAGE_LIFE_TIME
            )

            # Move the user into the waiting room if we can
            if isinstance(sender, User) or sender.voice is None:
                # If the command comes from DMs or the user is not connected to voice, instruct them to join
                logger.debug(f"{sender} enqueued themselves from DMs or user is not connected to voice")
                invite: Invite = await self.waiting_room.create_invite()
                await sender.send("Please join the waiting room until you are called on.\n"
                                  "**If you are not in the waiting room or breakout rooms when you are called on,"
                                  " you will be removed from the queue!**\n"
                                  f"{invite.url}",
                                  delete_after=GetConstants().MESSAGE_LIFE_TIME)
            else:
                await sender.move_to(self.waiting_room)
                await sender.send("I have moved you into the waiting room. **If you are not in the waiting room or \
        breakout rooms when you are called on, you will be removed from the queue!**")
                logger.debug(f"{sender} has been placed in the waiting room")

        else:
            logger.debug(f"{sender} was already in the queue and tried to enqueue themselves again")
            position = self.OHQueue.index(sender) + 1
            await sender.send(
                f"You are already in the queue. Please wait to be called\n"
                f"Current position: {position}",
                delete_after=GetConstants().MESSAGE_LIFE_TIME
            )

    async def _eq_elevated_queue(self, context: Context, student: str, instructor: str):
        """
        Manages the placing of a student into an instructor's elevated queue
        :param context: Object containing information about the caller
        :param student: The student that is being sent into another instructor's queue
        :param instructor: The instructor that the student is being sent to
        :return: None
        """

        member_conv = MemberConverter()
        try:
            student_id, instructor_id = await gather(member_conv.convert(context, student),
                                                     member_conv.convert(context, instructor))
            self.instructor_queue[instructor_id].put(student_id)
            print(self.instructor_queue)
            logger.debug(f"{context.author} has placed {student_id} into {instructor_id}'s queue")
        except BadArgument:
            logger.error(f"{context.author} gave the incorrect arguments"
                         f" for the eq command: {student} and {instructor}")
            await context.author.send("One of the users you entered is not a valid user")

    @commands.command(aliases=['leavequeue', 'lq'])
    async def leaveQueue(self, context: Context):
        """
        Removes caller from the queue
        @ctx: context object containing information about the caller
        """

        sender = context.author
        if sender in self.OHQueue:
            self.OHQueue.remove(sender)
            logger.debug(f"{sender} has been removed form the queue")
            await sender.send(f"{sender.mention} you have been removed from the queue")
        else:
            logger.debug(f"{sender} tried to leave the queue, but they were already not in the queue")
            await sender.send(f"{sender.mention} you were not in the queue")

    @commands.command(aliases=["dequeue", 'dq'])
    async def dequeueStudent(self, context: Context):
        """
        Dequeue a student from the queue and notify them
        @ctx: context object containing information about the caller
        """
        sender = context.author
        try:
            await isAdmin(context)
        except CommandPermissionError:
            logger.debug(f"{sender} was a student who called dq. This will trigger them to leave queue")
            await self.leaveQueue(context)
            return

        if isinstance(sender, User):
            logger.debug(f"{sender} attempted to dequeue from DMs but this isn't allowed")
            # If the command was sent via DM, tell them to do it from the bot channel instead
            await sender.send("Due to technical limitations, you must send the dequeue command from the server"
                              "channel",
                              delete_after=GetConstants().MESSAGE_LIFE_TIME)
            return

        if sender.voice is None:
            logger.debug(f"{sender} tried to deque but they were not in a voice channel")
            await sender.send(
                "You must be connected to a voice channel to do this. The queue has not been modified.")

        elif self.instructor_queue[sender]:
            student = self.instructor_queue[sender]
            logger.debug(f"{context.author} dequeud {student} from their personal queue")
            await self._dequeue_helper(context, student)

        elif len(self.OHQueue):
            student = self.OHQueue.pop(0)
            logger.debug(f"{student} has been dequeued")
            await self._dequeue_helper(context, student)

    async def _dequeue_helper(self, context: Context, student):
        sender = context.author
        if student.voice is None:
            logger.debug(f"{student} was not in the waiting when they were dequeued")
            await sender.send(
                f"{student.mention} is not in the waiting room or any of the breakout rooms. I cannot "
                "move them into your voice channel. They have been removed from the queue.",
                delete_after=GetConstants().MESSAGE_LIFE_TIME)
            # This one should not get a message timeout. The user may be afk
            await student.send(
                f"{student.mention} you have been called on but were not in the waiting room or any of the breakout"
                "rooms. I cannot move you into the office hours. You have been removed from the queue.",
            )
        else:
            await student.send(f"You are being summoned to {sender.mention}'s OH",
                               delete_after=GetConstants().MESSAGE_LIFE_TIME)
            # Add this student to the voice chat
            await student.move_to(sender.voice.channel)
            logger.debug(f"{student} has been summoned and moved to {sender.voice.channel}")


    @commands.command(aliases=["cq", "clearqueue"])
    @commands.check(isAdmin)
    async def clearQueue(self, context: Context):
        """
        Clears all students from the queue
        @ctx: context object containing information about the caller
        """
        sender = context.author
        self.OHQueue.clear()

        logger.debug(f"{sender} has cleared the queue")
        await sender.send("The queue has been cleared.")


def setup(bot):
    """
    This python file is an 'extension'. The setup file acts as the entry point to the extension.
    In our setup we load the cog we have written to be used in the discord bot
    """
    bot.add_cog(OH_Queue(bot))
