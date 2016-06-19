Getting started with BoaIRC
==============================
Welcome to the getting started with BoaIRC guide, it will (hopefully) help you understand how BoaIRC works.
As already mentioned on the main page, BoaIRC is really simple, all it does is to handle the IRC server connection
and a little bit of message parsing and dispatching.

BoaIRC is a threaded IRC library, that means that all the connection business is done on a different thread, not the
main thread, which allows your main thread to not block to receive or send messages. Additonally it's handler based,
which means that it parses the messages it gets from the server and will use handler functions that you can define
to do something with the message (or not). I call these **command handlers**, as they handle specific IRC commands.

What are command handlers?
--------------------------
Command handlers are just python functions which handle a specific IRC command, just like their name suggests.
A very simple command handler can look like this:

  def handler_PRIVMSG(self, line):
      prefix, command, params = line
      self.sendCommand('PONG :%s' % params[0])

