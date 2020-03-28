from logging import getLogger
from typing import Union
from main import DISCORD_GUILD_ID
from discord import Client, Member, User, Guild
from discord.ext import commands
from discord.ext.commands import Context
from discord.utils import get
from main import STUDENT, INSTRUCTOR_ROLE_ID, STUDENT_ROLE_ID

logger = getLogger(__name__)


# This will be resolved during cog setup
async def isAdmin(ctx: Context) -> bool:
    """
    Checks if the user who sent the command is an admin
    """
    sender = getSender(ctx)
    roles = None
    if isinstance(sender, User):
        # If the message is a DM, we need to look up the authors roles in the server
        client = roleManager.client

        guild = client.get_guild(DISCORD_GUILD_ID)
        if guild is None:
            # The guild was not in the cache, do an API call to fetch it
            guild = await client.fetch_guild(DISCORD_GUILD_ID)

        member = guild.get_member(sender.id)
        if member is None:
            member = await guild.fetch_member(sender.id)

        roles = member.roles
    else:
        # Otherwise, the message came from within the server. The roles can be extracted from the context
        roles = ctx.author.roles

    return any(role.id == INSTRUCTOR_ROLE_ID for role in roles)


def isStudent(ctx: Context) -> bool:
    """
    Checks if the user who sent the command is an student
    """
    for role in ctx.author.roles:
        if role.id == STUDENT_ROLE_ID:
            return True
    return False


def getSender(context: Context) -> Union[User, Member]:
    """
    Determines caller of message
    Returns caller as a user object
    """
    return context.author


class roleManager(commands.Cog):
    client = None

    def __init__(self, client: Client):
        roleManager.client = client

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
