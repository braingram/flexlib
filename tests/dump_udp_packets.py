#!/usr/bin/env python

import json
import sys
import time

import flexlib


ip = None
port = flexlib.smartsdr.connection.DEFAULT_PORT
udp_port = flexlib.vita.connection.DEFAULT_PORT
#udp_port = 4991
output_fn = '%s.json' % time.time()

if ip is None:
    if len(sys.argv) < 2:
        raise Exception(
            "An ip address must be supplied in the script or "
            "as the first argument")
    ip = sys.argv[1]

if len(sys.argv) > 2:
    fn = sys.argv[2]

sdr = flexlib.smartsdr.SmartSDR(ip, port)
sdr.send_command("client udpport %i" % udp_port)
sdr.send_command("display pan create x=100 y=100")

r = sdr.receive(timeout=0.25)
while r is not None:
    print r
    for a in dir(r):
        if a[:2] != '__':
            print a, getattr(r, a)
    r = sdr.receive(timeout=0.25)

vita = flexlib.vita.Vita(port=udp_port)
packets = []

#cid = flexlib.vita.const.VF_METER
cid = None

print("Starting grabbing packets: Ctrl-C to stop")
while True:
    try:
        packet = vita.receive()
        if packet is not None:
            if packet.header.class_id.packet_class_code != cid:
                packets.append(packet)
                print("Grabbed %i packets" % len(packets))
                print(packet.to_json())
            else:
                # print("skipping packet")
                pass
    except KeyboardInterrupt:
        print("Stopping grabbing...")
        break


if len(packets):
    print("Writing %s packets to %s" % (len(packets), output_fn))
    with open(output_fn, 'w') as f:
        json.dump(packets, f, default=lambda o: o.to_json())
