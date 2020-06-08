import sys
import discord
from discord.utils import find
from typing import *



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
        print(event)
        await client.logout()


    @client.event
    async def on_ready():
        with open(".env", 'w') as file:
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
                #"SMTP_HOST" :,
                #"TO" :,
                #"EMAIL" :,
                #"PASSWORD" :,
                #"CLASS" :,
            }



            for key, val in vars.items():
                writeVar(key, val, file)

        await client.logout()

    client.run(token)
    return 0



def writeVar(varName:str, val:str, file) -> None:
    alloc = f"{varName}={val}\n"
    file.write(alloc)
    



if __name__ == "__main__":
    exit(main(sys.argv[1]))
    