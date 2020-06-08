Help Cog
========

.. automodule:: cogs.help

.. autoclass:: cogs.help.Help


   .. py:method:: help_cmd(ctx: Context) -> None
        :async:

        Generalized help command that displays all command availible to the user.

        Invoked like: /help


   .. py:method:: queue_help(ctx: Context) -> None
        :async:

        Tells the user all commands that are pertinent to using the queue according to their acces level

        Invoked like: /help queue


   .. py:method:: refresh_help(ctx: Context) -> None
        :async:

        Utility refreshing the help in the help channel. Useful for when new commands get impletmented

        Invoked like: /help refreshhelp

   
