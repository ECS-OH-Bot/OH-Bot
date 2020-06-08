Tools Cog
=========

.. autoclass:: cogs.tools.Tools

   .. py:method:: clear(ctx: Context, amount: int=1) -> None
      :async:

      Deletes the number of most recent messages specified by amount, which defaults to just itself

   .. py:method:: on_member_join(member) -> None
      :async:

      On new student joining guild assign them student role and send them a welcome message