#!/usr/bin/env python

import select
import socket


DEFAULT_PORT = 4992


class TCP(object):
    MAX_SEQUENCE = 2 ** 32

    def __init__(self, ip, port):
        self.port = port
        self.ip = ip
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        self._receive_buffer = u""

    def send(self, msg):
        self.sock.send(msg)

    def receive(self, timeout=None, buffer_size=1024):
        if timeout is not None:
            r, _, _ = select.select([self.sock], [], [], timeout)
            if len(r) != 1:
                return None
        r = self.sock.receive(buffer_size)
        self._receive_buffer += r.decode('utf-8')
        # look for end of message '\n'
        if '\n' not in self._receive_buffer:
            return None
        e = self._receive_buffer.index('\n')
        sr = self._receive_buffer[:e]
        self._receive_buffer = self._receive_buffer[e+1:]
        return sr

    def __del__(self):
        self.sock.close()
