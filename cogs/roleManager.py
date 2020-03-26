import discord
from discord.ext import commands
from discord.utils import get

ADMIN="Instructor"
STUDENT="Student"
INSTRUCTOR_ROLE_ID=202921174290792458

def isAdmin(ctx) -> bool:
    for role in ctx.author.roles:
        if role.id == INSTRUCTOR_ROLE_ID:
            return True
    return False

class roleManager(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        On new student joining guild assign them student role
        """
        role = get(member.guild.roles, name=STUDENT)
        await member.add_roles(role)
        await member.send(f"{member.mention} has been promoted to the role Student")


def setup(client):
    """
    Called internally by discord API cog functionality
    I honestly have no idea how this works...
    """
    client.add_cog(roleManager(client))