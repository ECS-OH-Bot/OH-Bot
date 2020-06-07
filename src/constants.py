"""
Defines constants used across multiple files in this project.
Most of these constants are loaded from the environment variables
This singleton also holds parsed arguments
"""
from typing import Optional
import yaml
import re
import os

# Courtesy of:
# https://medium.com/swlh/python-yaml-configuration-with-environment-variables-parsing-77930f4273ac
def parse_config(path=None, data=None, tag='!ENV'):
    """
    Load a yaml configuration file and resolve any environment variables
    The environment variables must have !ENV before them and be in this format
    to be parsed: ${VAR_NAME}.
    
    :How to Use the !ENV directive in your config file:
        .. code-block:: yaml
        
            database:
                host: !ENV ${HOST}
                port: !ENV ${PORT}
            app:
                log_path: !ENV '/var/${LOG_PATH}'
                something_else: !ENV '${AWESOME_ENV_VAR}/var/${A_SECOND_AWESOME_VAR}'
    :param str path: the path to the yaml file
    :param str data: the yaml data itself as a stream
    :param str tag: the tag to look for
    :return: the dict configuration
    :rtype: dict[str, T]
    """
    # pattern for global vars: look for ${word}
    pattern = re.compile('.*?\${(\w+)}.*?')
    loader = yaml.SafeLoader

    # the tag will be used to mark where to start searching for the pattern
    # e.g. somekey: !ENV somestring${MYENVVAR}blah blah blah
    loader.add_implicit_resolver(tag, pattern, None)

    def constructor_env_variables(loader, node):
        """
        Extracts the environment variable from the node's value
        :param yaml.Loader loader: the yaml loader
        :param node: the current node in the yaml
        :return: the parsed string that contains the value of the environment
        variable
        """
        value = loader.construct_scalar(node)
        match = pattern.findall(value)  # to find all env variables in line
        if match:
            full_value = value
            for g in match:
                full_value = full_value.replace(
                    f'${{{g}}}', os.environ.get(g, g)
                )
            return full_value
        return value

    loader.add_constructor(tag, constructor_env_variables)

    if path:
        with open(path) as conf_data:
            return yaml.load(conf_data, Loader=loader)
    elif data:
        return yaml.load(data, Loader=loader)
    else:
        raise ValueError('Either a path or data should be defined as input')


class Constants:
    """
    Singleton accesible via GetConstants
    Below is the list of the variables you can access via the getter for this singleton

    :ivar str BOT_TOKEN: The API token for the bot
    :ivar int GUILD_ID: The ID for the server which the bot will be serving
    
    :ivar str WAITING_ROOM_CHANNEL_ID: Channel ID of the waiting room
    :ivar int QUEUE_CHANNEL_ID: Channel ID of the queue
    :ivar int ANNOUNCMENT_CHANNEL_ID: Channel ID of the announcement channel

    :ivar str ADMIN: Name for the admin role
    :ivar int INSTRUCTOR_ROLE_ID: Role ID for users that have the role of admin

    :ivar str STUDENT: Name for the student role
    :ivar int STUDENT_ROLE_ID: Role ID for users that have the role of student

    :ivar str CLASS: The name of the class that the bot is serving
    :ivar str COMMAND_CHAR: The character used to envoke commands, i.e. "/eq" where "/" is the command character
    :ivar str HELP_MESSAGES: The path to the YAML file which contains the various help messages
    :ivar str MESSAGE_LIFETIME: How long after sending the bot's DM's to users persist

    :ivar str LOGGING_DIR: The path to the directory where log files will be put in
    :ivar str LOGGING_CAPACITY: Maximum number of log files allowed in logging directory. If this amount is surpassed,
                            then the oldest log file will be deleted

    :ivar str SMTP_HOST: The smtp server used to send email notifications of fatal errors
    :ivar List[str] MAILING_LIST: List of email addresses to send critical alerts too
    
    :ivar str USERNAME: The email address that said notififcations will be sent form
    :ivar str PASSWORD: The password to the aforementioned email account

    Note that the above two should both specified in the .env file
    """
    instance: Optional['Constants'] = None

    def __init__(self, args):
        if Constants.instance is not None:
            raise RuntimeError("Cannot reinstantiate Constants singleton")

        config = parse_config(path=args.config)

        credentials = config["DiscordCredentials"]

        # The API token for the bot
        self.BOT_TOKEN = credentials["BotToken"]

        # The ID for the server
        self.GUILD_ID = int(credentials["GuildID"])

        channels = config["ChannelIDs"]

        # The ID for the waiting room and queue channels
        self.WAITING_ROOM_CHANNEL_ID = int(channels["WaitingRoom"])
        self.QUEUE_CHANNEL_ID = int(channels["Queue"])
        self.ANNOUNCEMENT_CHANNEL_ID = int(channels["Announcements"])

        # Roles
        admin = config["Roles"]["Admin"]
        self.ADMIN, self.INSTRUCTOR_ROLE_ID = admin["Name"], int(admin["RoleID"])

        student = config["Roles"]["Student"]
        self.STUDENT, self.STUDENT_ROLE_ID = student["Name"], int(student["RoleID"])

        bot_configs = config["BotConfigurations"]
        self.CLASS = bot_configs["ClassName"]
        self.COMMAND_CHAR = bot_configs["CommandCharacter"]
        self.HELP_MESSAGES = bot_configs["HelpMessage"]
        self.MESSAGE_LIFE_TIME = bot_configs["MessageLifetime"]

        # Logging
        logging = config["Logging"]
        self.LOGGING_DIR = logging["LoggingDir"]
        self.LOGGING_CAPACITY = logging["DirectoryCapacity"]

        # Email
        email = logging["Email"]
        self.SMTP_HOST = email["Smtp_host"]
        self.MAILING_LIST = email["To"]
        self.USERNAME = email["Credentials"][0]
        self.PASSWORD = email["Credentials"][1]

        # Program arguments
        self.args = args

        # Predefined constants


        Constants.instance = self

def GetConstants():
    """
    Function meant to access the instance of the singleton safely. Always use this after the singleton has been initialize

    :raises RuntimeError: Raised when the singleton has not first been instantiated
    :return: The instance of the singleton
    """
    if Constants.instance is not None:
        return Constants.instance
    else:
        raise RuntimeError("Attempt to access constants before singleton has been instantiated")