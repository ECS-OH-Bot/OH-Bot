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
    E.g.:
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