"""
Error types used by this bot
"""

from discord.ext.commands import CommandError


class CommandPermissionError(CommandError):
    """
    Raised when a non-elevated user attempts to invoke a command that requires special privileges
    """
    pass


class OHStateError(CommandError):
    """
    Raised when the expected OH state for a command is different from the actual state
    """
    pass


class OHQueueCommandUseError(CommandError):
    """
    Raised when a user incorrectly uses the queue
    """
