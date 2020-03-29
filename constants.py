"""
Defines constants used across multiple files in this project.
Most of these constants are loaded from the environment variables
This singleton also holds parsed arguments
"""
from typing import Optional
from dotenv import load_dotenv
from os import getenv
import argparse

class Constants:
    instance: Optional['Constants'] = None

    def __init__(self, args):
        if Constants.instance is not None:
            raise RuntimeError("Cannot reinstantiate Constants singleton")
        # Load variables from .env
        load_dotenv()

        # The API token for the bot
        self.BOT_TOKEN = getenv("BOT_TOKEN")

        # The ID for the server
        self.GUILD_ID = int(getenv("DISCORD_GUILD_ID"))

        # The ID for the waiting room and queue channels
        self.WAITING_ROOM_CHANNEL_ID = int(getenv("WAITING_ROOM_CHANNEL_ID"))
        self.QUEUE_CHANNEL_ID = int(getenv("QUEUE_CHANNEL_ID"))

        # Roles
        self.ADMIN = getenv("ADMIN")
        self.STUDENT = getenv("STUDENT")
        self.INSTRUCTOR_ROLE_ID = int(getenv("INSTRUCTOR_ROLE_ID"))
        self.STUDENT_ROLE_ID = int(getenv("STUDENT_ROLE_ID"))

        # Program arguments
        self.args = args

        # Predefined constants
        # Number of seconds a message should sit in the invoker's DMs
        # If this value is set to None, the message will not be deleted.
        self.MESSAGE_LIFE_TIME = None

        Constants.instance = self

def GetConstants():
    if Constants.instance is not None:
        return Constants.instance
    else:
        raise RuntimeError("Attempt to access constants before singleton has been instantiated")