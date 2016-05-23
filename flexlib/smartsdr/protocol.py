#!/usr/bin/env python


MAX_SEQUENCE_NUMBER = 2 ** 32


class ProtocolError(Exception):
    pass


class CommandBuilder(object):
    def __init__(self, debug=False):
        self.sequence_number = 0
        self.debug = debug

    def build(self, msg):
        if self.debug:
            s = u"CD"
        else:
            s = u"C"
        n = self.sequence_number
        s = u"%s%i|%s" % (s, n, msg)
        if s[-1] not in '\r\n':
            s += '\n'
        self.sequence_number += 1
        if self.sequence_number > MAX_SEQUENCE_NUMBER:
            self.sequence_number -= MAX_SEQUENCE_NUMBER
        return n, s.encode('utf-8')


class Response(object):
    def __init__(self, msg):
        pass


class Reply(Response):
    def __init__(self, msg):
        tokens = self.msg.strip().split('|')
        if len(tokens) < 3:
            raise ProtocolError("Invalid Reply tokens %s" % len(tokens))
        self.sequence_number = tokens[0][1:]
        try:
            self.hex_response = int(tokens[1], 16)
        except ValueError as e:
            raise ProtocolError(
                "Invalid Reply hex response [%s]: %s" % (tokens[1], e))
        self.message = tokens[2]
        if len(tokens) == 4:
            self.debug = tokens[3]
        else:
            self.debug = None


class Status(Response):
    def __init__(self, msg):
        tokens = self.msg.strip().split('|')
        if len(tokens) != 2:
            raise ProtocolError("Invalid Status tokens %s" % len(tokens))
        self.handle = tokens[0][1:]
        self.message = tokens[1]
        # TODO further parse message


class Handle(Response):
    def __init__(self, msg):
        self.value = msg[1:].strip()


class Version(Response):
    def __init__(self, msg):
        self.value = msg[1:].strip()


class Message(Response):
    def __init__(self, msg):
        tokens = self.msg.strip().split('|')
        if len(tokens) != 2:
            raise ProtocolError("Invalid Message tokens %s" % len(tokens))
        try:
            self.number = int(tokens[0][1:], 16)
        except ValueError as e:
            raise ProtocolError(
                "Invalid Message number [%s]: %s" % (tokens[1], e))
        self.message = tokens[1]
        # bits 24 and 25 of message contain severity
        # 0: info, 1: warning, 2: error, 3: fatal
        self.level = (self.number >> 24) & 0x3


responses = {
    'R': Reply,
    'S': Status,
    'H': Handle,
    'V': Version,
    'M': Message,
}


def parse_receive(msg):
    f = responses.get(msg[0], None)
    if f is None:
        raise ProtocolError("Invalid response key: %s" % (msg[0], ))
    return f(msg)
