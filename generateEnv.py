import sys
import discord
from discord.utils import find
from typing import *

ENV_FILE=".env"

def main(token:str) -> int:
    """
    Args:
        token (str): bot access token
    Return:
        exit code of main script
        NoneZero indicate a failure
    """
    client = discord.Client()

    @client.event
    async def on_error(event, *args, **kwargs):
        """
        Safely logout bot on event of unexpected error
        """
        print(event)
        await client.logout()
        exit(135)


    @client.event
    async def on_ready():
        """
        Gather Guild UIDs from guild the bot is instanciated to
        """
        print(f"Bare Instance of Bot established")
        print(f"Gathering Environment Variables....")
        with open(ENV_FILE, 'w') as file:
            writeVar("BOT_TOKEN", token, file)
            vars = {
                "GUILD_ID" : client.guilds[0].id,
                "QUEUE_ID" : find(lambda channel: channel.name == "oh-queue",client.get_all_channels()).id,
                "WAITING_ROOM_ID" : find(lambda channel: channel.name == "Waiting Room",client.get_all_channels()).id,
                "ANNOUNCEMENTS_ID" : find(lambda channel: channel.name == "announcements",client.get_all_channels()).id,
                "ADMIN_NAME": "Admin",
                "ADMIN_ROLE_ID" : find(lambda role : role.name == "Admin", client.guilds[0].roles).id,
                "STUDENT_NAME": "Student",
                "STUDENT_ROLE_ID" : find(lambda role : role.name == "Student", client.guilds[0].roles).id,
            }

            print(f"Variables Gathered, Writing...")

            for key, val in vars.items():
                writeVar(key, val, file)

        await client.logout()

    client.run(token)
    return 0



def writeVar(varName:str, val:str, file) -> None:
    """Formatter File wrapper

    Args:
        varName (str): environment variable to be exported
        val (str): value to be assigned to 
        file (FileObject): file we are writing to
    """
    alloc = f"export {varName}={val}\n"
    file.write(alloc)
    



if __name__ == "__main__":
    if sys.argv[2]:
        ENV_FILE=sys.argv[2]
    exit(main(sys.argv[1]))