# -*- coding: utf-8 -*-

from threading import Thread

from boa_irc_base import BoaIRCBase

class BoaIRC(BoaIRCBase):
    """
    This is a convenience class that can do often needed IRC tasks
    """

    buffer = []

    def __init__(self, host, nick, user, realname, password=None, port=6667, timeout=120):
        # Init parent base class
        BoaIRCBase.__init__(self, host, port, timeout)
        # Init instance variables
        self.nick           = nick
        self.user           = user
        self.realname       = realname
        self.password       = password
        self.authed         = False
        self._buffer        = []
        self._ping_thread   = Thread(target=self._ping_thread, args=(self.timeout/2,))
        self._ping_number   = 1

    def send(self, cmd):
        """Sends a raw IRC command (buffered)

        :param cmd: The command to send.
        :type cmd: str
        """
        if (self.authed == False):
            self._buffer.append(cmd)
        else:
            self.send_command(cmd)

    def quit(self, msg=None):
        """Quit connection to IRC server with optional message

        :param msg: The quit message (reason) that should be used.
        :type cmd: str
        """
        if (msg != None):
            self.send('QUIT :%s' % (msg))
        else:
            self.send("QUIT")

    def join(self, channel, password=None):                  # TODO: More then one channel/password (lists)
        """Join a channel

        :param channel: The channel to join to.
        :param password: Password (if any)
        :type channel: str
        :type password: str
        """
        if (password == None):
            self.send('JOIN %s' % (channel))
        else:
            self.send('JOIN %s %s' % (channel, pwd))

    def part(self, channel):                            # TODO: More then one channel (list)
        """Part (leave) a channel

        :param channel: The channel to leave.
        :type channel: str
        """
        self.send('PART %s' % (channel))

    def nick(self, nick):
        """Change nickname

        :param nick: New desired nickname.
        :type nick: str
        """
        self.send('NICK %s' % (nick))

    def _send_buffer(self):
        for line in self._buffer:
            self.send(line)
        self.buffer = []

    # Ping thread related commands
    def _ping_thread(self, interval):
        while ((self._ping_number > 0) and self.is_connected and self.authed is True):
            time.sleep(interval)
            self.send_command('PING :' + self._ping_number)
        return False

    def _start_ping_thread(self):
        self._ping_number = 1
        self._ping_thread.daemon = True
        self._ping_thread.start()

    def _stop_ping_thread(self):
        self._ping_number = 0

    def _on_connect(self):
        self._auth()
        self._start_ping_thread()

    def _auth(self):
        if (self.password != None):
            self.send_command('PASS %s' % (self.password))
        self.send_command('NICK %s' % (self.nick))
        self.send_command('USER %s 0 * :%s' % (self.user, self.realname))

    def _handler_001(self, line):
        self.authed = True
        self._send_buffer()

    def _handler_PING(self, line):
        prefix, command, params = line
        self.send_command('PONG :%s' % params[0])


