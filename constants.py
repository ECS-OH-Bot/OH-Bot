"""
Defines constants used across multiple files in this project.
Most of these constants are loaded from the environment variables
This singleton also holds parsed arguments
"""
from typing import Optional
import yaml
from os import getenv
import argparse


class Constants:
    instance: Optional['Constants'] = None

    def __init__(self, args):
        if Constants.instance is not None:
            raise RuntimeError("Cannot reinstantiate Constants singleton")
        # Load variables from .env
        with open(args.config) as config_file:
            config = yaml.safe_load(config_file)

        credentials = config["DiscordCredentials"]

        # The API token for the bot
        self.BOT_TOKEN = credentials["BotToken"]

        # The ID for the server
        self.GUILD_ID = credentials["GuildID"]

        channels = config["ChannelIDs"]

        # The ID for the waiting room and queue channels
        self.WAITING_ROOM_CHANNEL_ID = channels["WaitingRoom"]
        self.QUEUE_CHANNEL_ID = channels["Queue"]
        self.ANNOUNCEMENT_CHANNEL_ID = channels["Announcements"]

        # Roles
        admin = config["Roles"]["Admin"]
        self.ADMIN, self.INSTRUCTOR_ROLE_ID = admin["Name"], admin["RoleID"]

        student = config["Roles"]["Admin"]
        self.STUDENT, self.STUDENT_ROLE_ID = student["Name"], student["RoleID"]

        bot_configs = config["BotConfigurations"]
        self.COMMAND_CHAR = bot_configs["CommandCharacter"]
        self.HELP_MESSAGES = bot_configs["HelpMessage"]
        self.MESSAGE_LIFE_TIME = bot_configs["MessageLifetime"]

        # Logging
        logging = config["Logging"]
        self.LOGGING_DIR = logging["LoggingDir"]
        self.LOGGING_CAPACITY = logging["DirectoryCapacity"]

        # Program arguments
        self.args = args

        # Predefined constants


        Constants.instance = self

def GetConstants():
    if Constants.instance is not None:
        return Constants.instance
    else:
        raise RuntimeError("Attempt to access constants before singleton has been instantiated")