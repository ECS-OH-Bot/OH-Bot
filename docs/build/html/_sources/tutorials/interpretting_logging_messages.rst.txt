How to Make Use of Log Messages
===============================

When running a live service that you cannot constantly monitor, it is essential that you keep a record of what has happened, so
that you can backtrack to pinpoint where problems happened. This bot accomplishes this using 
`Python's builtin logging module <https://docs.python.org/3/howto/logging.html>`_


How We Do Logging
-----------------

Our log messages have been configured to display the date, the time (in the form HH:MM:SS,sss, where sss represents microseconds),
what file and what line the statement came from, i.e. :code:`<file_name>:<line_number>`, the level of the message, either DEBUG, 
INFO, WARNING, ERROR, or CRITICAL, in order of asscending severity, and then the log message, which should give a concise statement
regarding what happened. We record these messages in three ways.


1. Log File
^^^^^^^^^^^

All logging statements are put into a log file. This log file is located in whatever directory was specified in the config file.
Note that this log file is set to "rollover" at midnight so long as it's running. This means that in a live deployment that you'll
have one log file per day. After seven days, the oldest log file gets deleted so as to not clutter up the directory.


2. Standard Output
^^^^^^^^^^^^^^^^^^

As with the log file, all log statement are printed to stdout. This is very useful for testing and debugging purposes. Morevoer, services
like Azure, the one we used for hosting, allow you to view the realtime output of what your hosting, which makes it very useful if you
ever have that nightmare scenario of trying to find a bug in production


3. Email Notification
^^^^^^^^^^^^^^^^^^^^^

Lastly, you have a life; you're not going to sit around looking at log output all day to know if something failed catastrophically, i.e. an
error went unhandled. So we've setup a system, where you can give your email and password (note that you should be using an 
`app password <https://support.google.com/accounts/answer/185833?hl=en>`_ if you're using Gmail. I would advise against using your real password),
and the bot will email everyon on the mailing list given in the config file in the event that an exception occurs and was left unhandled.





