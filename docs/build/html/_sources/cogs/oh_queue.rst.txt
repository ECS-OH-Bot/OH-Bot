OH Queue Cog
============

The logic for how we handle the dequeue operation is best described by the following flow cahrt

.. image:: ../queue_flow.png
   :scale: 50 %

.. autoclass:: cogs.oh_queue.OH_Queue

   .. py:method:: onQueueUpdate() -> None
      :async:

      Update the persistant queue message based on _OHQueue

   .. py:method:: enterQueue(context: Context) -> None
      :async:

      Enters user into the OH queue. If they already are enqueued return them their position in queue

      Invoked like: /eq

   .. py:method:: leaveQueue(context: Context) -> None
      :async:

      Removes caller from the queue

      Invoked like: /lq

   .. py:method:: dequeueStudent(context: Context) -> None
      :async:

      Dequeue a student from the queue and notify them

      Invoked like: /dq

   .. py:method:: clearQueue(context: Context) -> None
      :async:

      Clears all students from the queue

      Invoked like: /cq
   


