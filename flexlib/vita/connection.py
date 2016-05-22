#!/usr/bin/env python

import select
import socket

DEFAULT_PORT = 4991
DEFAULT_IP = ""


class UDP(object):
    #FlexLib/API.cs:112
    def __init__(self, ip=DEFAULT_IP, port=DEFAULT_PORT):
        self.port = port
        self.ip = ip
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))

    #Vita/VitaFlex.cs:33
    def receive(self, timeout=None, buffer_size=65535):
        """Returns (data, addr)"""
        if timeout is not None:
            r, _, _ = select.select([self.sock], [], [], timeout=timeout)
            if len(r) != 1:
                return None
        return self.sock.recvfrom(buffer_size)

    def __del__(self):
        self.sock.close()


#def run_process(out_queue, ip=DEFAULT_IP, port=DEFAULT_PORT):
#    conn = UDP(ip, port)
#    while True:
#        msg = conn.receive()
#        out_queue.put(msg)
#    del conn


#class UDPProcess(object):
#    def __init__(self, ip=DEFAULT_IP, port=DEFAULT_PORT):
#        pass
