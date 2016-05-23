#!/usr/bin/env python

from . import smartsdr
from . import vita


__all_ = ['smartsdr', 'vita']


class Flex(object):
    def __init__(self):
        self.vita = vita.Vita()
        self.smartsdr = smartsdr.SmartSDR()
