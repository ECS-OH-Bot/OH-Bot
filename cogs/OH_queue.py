import discord
from discord.ext import commands

class OH_Queue(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._OHQueue = dict()

    @commands.command(aliases=["listqueue", "lsq"])
    async def listQueue(self, ctx):
        msg = ''
        for _, name in self._OHQueue:
            name = str(name)
            name.join("\n")
            msg.join(name)

        print(msg)

    @commands.command(aliases=["enterqueue", "eq"])
    async def enterQueue(self, ctx: discord.ext.commands.context.Context):
        sender = ctx.author
        self._OHQueue[sender.id] = sender._user
        await ctx.send(f"<@{sender.id}> you have been added to the queue")
        # Call the list queue function to let them know where they stand in the queue
        #self.listQueue(ctx)


    @commands.command(aliases=['leavequeue', 'lq'])
    async def leaveQueue(self, ctx):
        pass


def setup(client):
    client.add_cog(OH_Queue(client))