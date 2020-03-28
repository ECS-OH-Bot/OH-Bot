from typing import Optional

import discord
from discord import Client, TextChannel, DMChannel, Permissions
from discord.ext import commands
from discord.ext.commands.context import Context
from .roleManager import isAdmin, getSender
from main import QUEUE_CHANNEL_ID, DISCORD_GUILD_ID
from cogs.tools import selfClean

class OH_Queue(commands.Cog):

    def __init__(self, client: Client):
        self.client = client
        self.OHQueue = list()
        self.admins = list()
        # Reference to TextChannel is resolved by the pre invoke hook
        self.queue_channel: Optional[TextChannel] = None

    async def cog_before_invoke(self, context: Context) -> None:
        if self.queue_channel is None:
            self.queue_channel = self.client.get_channel(QUEUE_CHANNEL_ID)

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

        sender = getSender(context)
        if sender in self.OHQueue:
            self.OHQueue.remove(sender)
            await sender.send(f"{sender.mention} you have been removed from the queue")
        else:
            await sender.send(f"{sender.mention} you were not in the queue")
        await selfClean(context)



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
        await selfClean(context)


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
        await selfClean(context)

    @commands.group()
    async def queue(self, context: Context):
        pass

    # This is a subcommand of queue
    # invoked by >queue help
    # you may want to move this back to a cog command instead of a subcommand
    @queue.command()
    async def help(self, context: Context):
        embed = discord.Embed(title="Help", description="", color=0x7289da)
        embed.set_author(
            name="OH Bot",
            url="https://discordbots.org/bot/472911936951156740",
            icon_url="https://i.imgur.com/i7vvOo5.png"
        )

        embed.add_field(
            name=f'**Commands**',
            value=f'**Enter the OH queue by using the following command:**\n\n`>enterqueue or >eq`\n\n------------\n\n'
                  f'**Leave the OH queue by using the following command:**\n\n`>leavequeue or >lq`\n\n------------\n\n',
            inline=False
        )
        if isAdmin(context):
            adminEmbed = discord.Embed(title="Admin Help", description="", color=0x7289da)
            adminEmbed.set_author(
                name="OH Bot",
                url="https://discordbots.org/bot/472911936951156740",
                icon_url="https://i.imgur.com/i7vvOo5.png"
            )
            adminEmbed.add_field(
                name=f"**Admin only commands",
                value=f'**Clear the OH queue by using the following command:**\n\n`>leavequeue or >lq`\n\n------------\n\n'
                      f'**Call a student into your OH session by using the following command:**\n\n`>dequeue or >dq`\n\n------------\n\n',
                inline=False
            )
        await getSender(context).send(embed=embed)
        await selfClean(context)


def setup(client):
    """
    This python file is an 'extension'. The setup file acts as the entry point to the extension.
    In our setup we load the cog we have written to be used in the discord bot
    """
    client.add_cog(OH_Queue(client))