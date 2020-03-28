from typing import Union, Optional
from main import DISCORD_GUILD_ID
from discord import Client, Member, User, Guild
from discord.ext import commands
from discord.ext.commands import Context
from discord.utils import get
from main import STUDENT, INSTRUCTOR_ROLE_ID, STUDENT_ROLE_ID


async def getGuildMemberFromUser(user: User) -> Optional[Member]:
    """
    Resolves a user into a member of the guild
    :param user: The user instance
    :return: The member instance, or None if the user is not a member of the guild
    """
    client = roleManager.client

    # Retrieve the guild and member, from cache preferably.

    guild = client.get_guild(DISCORD_GUILD_ID)
    if guild is None:
        guild = await client.fetch_guild(DISCORD_GUILD_ID)

    member = guild.get_member(user.id)
    if member is None:
        member = await guild.fetch_member(user.id)

    return member

async def isAdmin(ctx: Context) -> bool:
    """
    Checks if the user who sent the command is an admin
    """
    sender = getSender(ctx)
    roles = None
    if isinstance(sender, User):
        # If the message is a DM, we need to look up the authors roles in the server
        member = await getGuildMemberFromUser(sender)

        if member is None:
            return False
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
