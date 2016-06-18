#!/usr/bin/env python

import sys

import pcapng
import scapy.layers.l2
import scapy.layers.inet

import flexlib


fn = 'FlexCapture.pcapng'
if len(sys.argv) > 2:
    fn = sys.argv[1]

dst_address = '10.0.1.44'

packets = []
with open(fn, 'r') as fp:
    scanner = pcapng.FileScanner(fp)
    for b in scanner:
        if isinstance(b, pcapng.blocks.EnhancedPacket):
            e = scapy.layers.l2.Ether(b.packet_data)
            p1 = e.payload
            if isinstance(p1, scapy.layers.inet.IP):
                p2 = p1.payload
                if isinstance(p2, scapy.layers.inet.TCP):
                    pass
                elif isinstance(p2, scapy.layers.inet.UDP):
                    if p1.dst == dst_address and p1.dport == 4991:
                        flp = flexlib.vita.protocol.parse_packet(
                            p2.payload.original)
                        packets.append(flp)
                        if len(packets) > 10:
                            break
