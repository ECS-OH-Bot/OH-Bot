import discord
from discord.ext import commands

class OH_Queue(commands.Cog):

    def __init__(self, client):
        self.client = client



def setup(client):
    client.add_cog(OH_Queue(client))