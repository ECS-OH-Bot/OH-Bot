import discord
from discord.ext import commands
from discord.utils import get

ADMIN="Instructor"
STUDENT="Student"
INSTRUCTOR_ROLE_ID=202921174290792458
STUDENT_ROLE_ID=692258575241707560

def isAdmin(ctx) -> bool:
    """
    Checks if the user who sent the command is an admin
    """
    for role in ctx.author.roles:
        if role.id == INSTRUCTOR_ROLE_ID:
            return True
    return False

def isStudent(ctx) -> bool:
    """
    Checks if the user who sent the command is an admin
    """
    for role in ctx.author.roles:
        if role.id == STUDENT_ROLE_ID:
            return True
    return False

class roleManager(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.channel = None  # This will be populated later in execution

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        On new student joining guild assign them student role
        """
        role = get(member.guild.roles, name=STUDENT)
        await member.add_roles(role)
        await member.send(f"{member.mention} welcome! You have been promoted to the role of Student")


def setup(client):
    """
    Called internally by discord API cog functionality
    I honestly have no idea how this works...
    """
    client.add_cog(roleManager(client))