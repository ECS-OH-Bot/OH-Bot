import discord
from discord.ext import commands

class NetTools(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"OH Bot connected")

    #Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.client.latency * 1000)}")


def setup(client):
    client.add_cog(NetTools(client))