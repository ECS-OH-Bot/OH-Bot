import discord
from discord.ext import commands

class OH_Queue(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._OHQueue = list()

    @commands.command(aliases=["listqueue", "lsq"])
    async def listQueue(self, ctx):
        msg = ''
        for user in self._OHQueue:
            name = user.name + '\n'
            msg += name

        await ctx.send(f"Current users in queue: {msg}")

    @commands.command(aliases=["enterqueue", "eq"])
    async def enterQueue(self, ctx: discord.ext.commands.context.Context):
        sender = ctx.author._user
        self._OHQueue.append(sender)
        await ctx.send(f"{sender.mention} you have been added to the queue")
        # Call the list queue function to let them know where they stand in the queue
        #self.listQueue(ctx)


    @commands.command(aliases=['leavequeue', 'lq'])
    async def leaveQueue(self, ctx):
        pass


def setup(client):
    client.add_cog(OH_Queue(client))