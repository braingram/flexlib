#!/usr/bin/env python

from . import connection
from . import protocol


class Vita(object):
    def __init__(
            self, ip=connection.DEFAULT_IP, port=connection.DEFAULT_PORT):
        self.conn = connection.UDP(ip, port)

    def __del__(self):
        if hasattr(self, 'conn'):
            del self.conn

    def receive(self, timeout=None):
        data_addr = self.conn.receive(timeout=timeout)
        if data_addr is None:
            return None
        packet = protocol.parse_packet(data_addr[0])
        return packet
