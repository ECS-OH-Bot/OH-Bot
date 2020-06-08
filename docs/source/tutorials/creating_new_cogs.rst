Creating New Cogs
=================

What is a Cog?
--------------

In the words of the `Discord API docs <https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Cog>`_, a cog is
"a collection of commands, listeners, and optional state to help group commands together". A more intuitive way to think of what a cog is to
recall what a cog is in a machine: an individual component that serves some purpose within the machine. Cogs are a nice way to think of grouping
toghether functionalities that the bot should have.

How Can I Set Up a Cog?
-----------------------

#. Create a new python module in the :code:`src/cogs/` cogs directory.

#. Open the aforementioned file in your editor of choice and do the following

   #. Copy and paste this expression to initialize logging for the module: :code:`logger = getLogger(f"main.{__name__}")`

   #. Define a class that inherits from :code:`commands.Cog` and defines its constructor as the following:
    .. code-block:: python 
            
        def __init__(self, client):
            self.client = client  

   #. To define a new command, create an asynchronous method and decorate it with the 
      `@commands.command <https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=commands%20command#discord.ext.commands.command>`_
      decorator
    
That's it. To pull it all toghether by definining a cog that replys "hello" when the user types the command "/hi" and logs the user that
entered the command

.. code-block:: python

    from logging import getLogger

    from discord.ext import commands
    from discord.ext.commands import Bot
    from discord.ext.commands.context import Context

    class Hello(commands.Cog):

        def __init__(self, client: Bot):
            self.client = client

        @commands.command(alias=['hi'])
        async def say_hello(self, ctx: Context):
            sender = ctx.author
            await sender.send("hello")
            logger.debug(f"{sender} said hi")




