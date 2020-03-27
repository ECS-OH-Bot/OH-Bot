from discord.ext import commands
from discord.ext.commands import Context
from discord.utils import get
from main import STUDENT, INSTRUCTOR_ROLE_ID, STUDENT_ROLE_ID


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

def getSender(context: Context):
    """
    Determines caller of message
    Returns caller as a user object
    """
    return context.author

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