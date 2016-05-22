#!/usr/bin/env python

#import multiprocessing
import select
import socket

#from . import protocol

DEFAULT_PORT = 4992


class TCP(object):
    MAX_SEQUENCE = 2 ** 32

    def __init__(self, ip, port):
        self.port = port
        self.ip = ip
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        #self.sequence_number = 0
        #self.debug = debug
        #self.reply_callbacks = {}
        self._receive_buffer = u""

    #def send(self, msg, reply_callback=None):
    def send(self, msg):
        #if self.debug:
        #    s = u"CD"
        #else:
        #    s = u"C"
        #s = u"%s%i|%s" % (
        #    s,
        #    self.sequence_number,
        #    msg)
        #if s[-1] not in '\r\n':
        #    s += '\n'
        #self.sock.send(s.encode('utf-8'))
        self.sock.send(msg)
        #if reply_callback is not None:
        #    self.reply_callbacks[self.sequence_number] = reply_callback
        #self.sequence_number += 1
        #if self.sequnce_number >= self.MAX_SEQUENCE:
        #    self.sequence_number -= self.MAX_SEQUENCE

    def receive(self, buffer_size=1024, timeout=None):
        if timeout is not None:
            r, _, _ = select.select([self.sock], [], [], timeout=timeout)
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
        # return protocol.parse_receive(sr)
        return sr

    def __del__(self):
        self.sock.close()


#def run_process(in_queue, out_queue, ip, port=DEFAULT_PORT, timeout=0.001):
#    conn = TCP(ip, port)
#    while True:
#        try:
#            cmd = in_queue.get(False, timeout)
#            if cmd is None:
#                break
#            conn.send(cmd)
#        except multiprocessing.Queue.Empty:
#            pass
#        msg = conn.recieve(block=False)
#        if msg is not None:
#            out_queue.put(msg)
#    del conn


#class TCPProcess(object):
#    def __init__(self, ip, port=DEFAULT_PORT, timeout=0.001):
#        self.inq = multiprocessing.Queue()
#        self.outq = multiprocessing.Queue()
#        self.process = multiprocessing.Process(
#            target=run_process,
#            args=(self.inq, self.outq, ip, port, timeout))
#        self.process.start()
#        self.ip = ip
#        self.port = port
#        self.timeout = timeout
#
#    def send(self, msg):
#        self.inq.put(msg)
#
#    def receive(self, timeout=None):
#        if timeout is None:
#            timeout = self.timeout
#        try:
#            return self.outq.get(False, timeout)
#        except multiprocessing.Queue.Empty:
#            return None
#
#    def __del__(self):
#        self.inq.put(None)
#        self.process.join()
