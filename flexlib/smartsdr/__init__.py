#!/usr/bin/env python

from . import connection
from . import protocol


class SmartSDR(object):
    def __init__(self, ip, port=connection.DEFAULT_PORT):
        self.conn = connection.TCP(ip, port)
        self.version = None
        self.handle = None
        self.callbacks = {}
        self._cmd_builder = protocol.CommandBuilder()

    def __del__(self):
        if hasattr(self, 'conn'):
            del self.conn

    def send_command(self, msg, callback=None):
        sn, cmd = self._cmd_builder.build(msg)
        self.conn.send(cmd)

    def receive(self, timeout=None):
        msg = self.conn.receive(timeout=timeout)
        if msg is None:
            return None
        r = protocol.parse_receive(msg)
        if isinstance(r, protocol.Version):
            self.version = r.value
        elif isinstance(r, protocol.Handle):
            self.handle = r.value
        elif isinstance(r, protocol.Reply):
            self.new_reply(r)
        elif isinstance(r, protocol.Status):
            self.new_status(r)
        elif isinstance(r, protocol.Message):
            self.new_message(r)
        else:
            raise protocol.ProtocolError(
                "Unknown response: %s" % r)
        return r

    def new_reply(self, reply):
        # check that command was completed successfully
        # process callback
        pass

    def new_status(self, status):
        pass

    def new_message(self, message):
        pass
