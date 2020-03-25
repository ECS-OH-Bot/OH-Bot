import discord
from discord.ext import commands

class NetTools(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"OH Bot connected")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        """
        Error event handler
        Currently handling for err is None
        @ctx: context object containing information about the caller
        @err: error object raised by caller
        Error types currently handled:
        CommandNotFound,
        """
        sender = ctx.author._user
        if isinstance(err, commands.CommandNotFound):
            await ctx.send(
                f"Command '{ctx.invoked_with}' does not exist\n"
                f"{sender.mention} check your spelling"
            )

    #Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.client.latency * 1000)}")



def setup(client):
    """
    Called internally by discord API cog functionality
    I honestly have no idea how this works...
    """
    client.add_cog(NetTools(client))