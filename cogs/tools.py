from discord.ext import commands

class Tools(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=1):
        """
        By default this command will delete the message that calls it
        @ctx: context object containing information about the caller
        @amount
        """
        await ctx.channel.purge(limit=amount)

def setup(client):
    """
    Called internally by discord API cog functionality
    I honestly have no idea how this works...
    """
    client.add_cog(Tools(client))