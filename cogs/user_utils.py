"""
Utility functions for working with user and member instances
"""
from typing import Optional
from discord.ext import commands
from discord import User, Member
from constants import GetConstants

class UserUtils(commands.Cog):
    bot: Optional[commands.Bot] = None

    @classmethod
    async def userToMember(cls, user: User) -> Optional[Member]:
        """
        Resolves a user into a member of the guild
        When the bot recieves a direct message the author of the message is a User
        To get information about this user as a member of a guild, a member instance is needed
        :param user: The user instance
        :return: The member instance, or None if the user is not a member of the guild
        """
        guild = cls.bot.get_guild(GetConstants().DISCORD_GUILD_ID)
        if guild is None:
            guild = await cls.bot.fetch_guild(GetConstants().DISCORD_GUILD_ID)

        member = guild.get_member(user.id)
        if member is None:
            member = await guild.fetch_member(user.id)

        return member

    @classmethod
    async def isAdmin(cls, context: commands.Context) -> bool:
        """
        Returns true if context.author has the Admin role, false otherwise
        This is used with the @command.check decorator to facilitate authentication for elevated commands
        """
        roles = None
        if isinstance(context.author, User):
            # If the message is a DM, we need to look up the authors roles in the server
            member = await cls.userToMember(context.author)

            if member is None:
                return False
            roles = member.roles
        else:
            # Otherwise, the message came from within the server. The roles can be directly extracted from the context
            roles = context.author.roles

        return any(role.id == GetConstants().INSTRUCTOR_ROLE_ID for role in roles)

    @classmethod
    async def isStudent(cls, context: commands.Context) -> bool:
        """
        Returns true if context.author has the Student role, false otherwise
        """
        roles = None
        if isinstance(context.author, User):
            # If the message is a DM, we need to look up the authors roles in the server
            member = await cls.userToMember(context.author)

            if member is None:
                return False
            roles = member.roles
        else:
            # Otherwise, the message came from within the server. The roles can be directly extracted from the context
            roles = context.author.roles

        return any(role.id == GetConstants().STUDENT_ROLE_ID for role in roles)

def setup(bot: commands.Bot) -> None:
    UserUtils.bot = bot
