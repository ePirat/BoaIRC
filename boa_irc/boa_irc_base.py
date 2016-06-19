# -*- coding: utf-8 -*-

import socket

from threading import Thread
from enum import Enum

class MetaCommands(Enum):
    all         = 0
    on_connect  = 1

class BoaIRCBase():
    """
    This is the underlying base class of BoaIRC, which manages the connection
    and other relvant server-related states.

    It provides no handlers whatsoever, not even PING handling so you should
    provide those yourself either in a Class inheriting from BoaIRCBase or
    just by registering the necessary handlers.

    Args:
        host (str): Hostname or IP of the IRC server
        port (Optional[int]): Server port. Defaults to 6667.
        timeout (Optional[int]): Timeout in seconds for the IRC connection. Defaults to 120.

    Returns:
        BoaIRCBase: An initialized BoaIRCBase instance.
    """

    _crlf   = '\r\n'
    _space  = ' '
    _sep    = ':'

    _active = True

    def __init__(self, host, port=6667, timeout=120):
        self.id         =   id(self)    #: Indentifies the :class:`BoaIRCBase` instance
        self.host       =   host        #: Host or IP of the IRC server
        self.port       =   port        #: Port of the IRC server
        self.timeout    =   timeout     #: Connection timeout
        self.connection =   False
        self._thread    =   Thread(target=self._con_thread)
        self._handlers  =   {}
        self._data      =   ''

    def connect(self, daemon=True):
        """Connect to the irc server

        Args:
            daemon (bool): Use daemon mode for the connection thread.
        """
        self._thread.daemon = daemon
        self._thread.start()

    def is_connected(self):
        """Indicates if we are successfully connected

        Returns:
            bool: True if connected, else False.
        """
        return self._thread.is_alive()

    def register_handler(self, command, callback):
        """Register a command handler

        Args:
            command (str): Command for which to register the handler.
            callback(function): The command handler function.
        """
        self._handlers[command] = callback

    def unregister_handler(self, command):
        """Unregister a command handler

        Args:
            command (str): The command for which to unregister the handler.
        """
        if command in self._handlers:
            self._handlers.remove(command)

    def send_command(self, cmd):
        self.connection.send(cmd + self._crlf)

    def send_chars(self, chars):
        self.connection.send(chars)

    def disconnect(self):
        """Disconnect from the server"""
        self._active = False
        self.connection.close()

    # Implement this in subclasses to do something on connect
    def _on_connect(self):
        pass

    def _con_thread(self):
        self.connection = socket.create_connection((self.host, self.port))
        self.connection.settimeout(self.timeout)
        self._on_connect()
        self._handle_on_connect()
        while (self._active):
            data = self.connection.recv(1024)
            if data:
                lines = self._parse_stream(data)
                lines = map(self._parse_line, lines)
                for line in lines:
                    self._dispatch_line(line)

    def _dispatch_line(self, line):
        prefix, command, params = line
        self._handle_all(line)
        if hasattr(self, '_handler_' + command):
            handle = getattr(self, '_handler_' + command)
            next = lambda l=line: handle(l)
        else:
            next = lambda l=None: None
        if command in self._handlers:
            self._handlers[command](self, line, next)
        else:
            next()

    def _handle_on_connect(self):
        next = lambda l=None: None
        line = (None, None, None)
        if MetaCommands.on_connect in self._handlers:
            self._handlers[MetaCommands.on_connect](self, line, next)

    def _handle_all(self, line):
        next = lambda l=None: None
        if MetaCommands.all in self._handlers:
            self._handlers[MetaCommands.all](self, line, next)

    def _parse_line(self, message):
        prefix  = None
        command = None
        params  = None
        line    = message.split(None, 1)
        if (len(line) < 2):
            return False
        if (line[0][0] == self._sep):
            prefix  = line[0][1:]
            line    = line[1].split(None, 1)
            command = line[0]
        else:
            command = line[0]
        if (line[1][0] == self._sep):
            params = [line[1][1:]]
        else:
            params = line[1].split(self._space + self._sep, 1)
            middle = params[0].split()
            if (len(params) < 2):
                params      = middle
            else:
                params      = middle + [params[1]]
        return (prefix, command, params)

    def _parse_stream(self, data):
        self._data += data
        lines = self._data.split(self._crlf)
        self._data = lines[-1]
        return lines[:-1]
