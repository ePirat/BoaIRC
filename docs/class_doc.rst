Class Documentation
====================

The BoaIRC class
----------------
.. autoclass:: boa_irc.BoaIRC
   :members:

Command handler function
------------------------
.. py:function:: handle_FOO(caller, line, default)

   This is an example command handler function, it is called with the following
   arguments:

   :param caller: The calling BoaIRCBase (or BoasIRC) instance
   :type caller: BoaIRCBase
   :param line: A tuple of ``(prefix command, params)``
   :type line: tuple
   :param default: The default event handler lambda
   :type default: lambda

The BoaIRCBase class
---------------------
.. autoclass:: boa_irc.BoaIRCBase
   :members:
