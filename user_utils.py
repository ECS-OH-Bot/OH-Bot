"""
Utility functions for working with user and member instances
"""
from typing import Optional
from discord.ext import commands
from discord import User, Member

from constants import GetConstants
from errors import CommandPermissionError

async def userToMember(user: User, bot: commands.Bot) -> Optional[Member]:
    """
    Resolves a user into a member of the guild
    When the bot receives a direct message the author of the message is a User
    To get information about this user as a member of a guild, a member instance is needed
    :param user: The user instance
    :param bot: An instance of the bot
    :return: The member instance, or None if the user is not a member of the guild
    """
    guild = bot.get_guild(GetConstants().GUILD_ID)
    if guild is None:
        guild = await bot.fetch_guild(GetConstants().GUILD_ID)

    member = guild.get_member(user.id)
    if member is None:
        member = await guild.fetch_member(user.id)

    return member


async def isAdmin(context: commands.Context) -> bool:
    """
    Returns true if context.author has the Admin role, false otherwise
    This is used with the @command.check decorator to facilitate authentication for elevated commands
    """
    roles = None
    if isinstance(context.author, User):
        # If the message is a DM, we need to look up the authors roles in the server
        member = await userToMember(context.author, context.bot)

        if member is None:
            return False
        roles = member.roles
    else:
        # Otherwise, the message came from within the server. The roles can be directly extracted from the context
        roles = context.author.roles

    if not any(role.id == GetConstants().INSTRUCTOR_ROLE_ID for role in roles):
        return False # CommandPermissionError()
    return True

async def isStudent(context: commands.Context) -> bool:
    """
    Returns true if context.author has the Student role, false otherwise
    """
    roles = None
    if isinstance(context.author, User):
        # If the message is a DM, we need to look up the authors roles in the server
        member = await context.bot.userToMember(context.author, context.bot)

        if member is None:
            return False
        roles = member.roles
    else:
        # Otherwise, the message came from within the server. The roles can be directly extracted from the context
        roles = context.author.roles

    return any(role.id == GetConstants().STUDENT_ROLE_ID for role in roles)