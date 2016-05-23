#!/usr/bin/env python

import json
import sys
import time

import flexlib


ip = None
port = flexlib.smartsdr.connection.DEFAULT_PORT
udp_port = flexlib.vita.connection.DEFAULT_PORT
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

vita = flexlib.vita.Vita(port=udp_port)
packets = []

print("Starting grabbing packets: Ctrl-C to stop")
while True:
    try:
        packet = vita.receive()
        if packet is not None:
            packets.append(packet)
            print("Grabbed %i packets" % len(packets))
    except KeyboardInterrupt:
        print("Stopping grabbing...")
        break


if len(packets):
    print("Writing %s packets to %s" % (len(packets), output_fn))
    with open(output_fn, 'w') as f:
        json.dump(packets, f, default=lambda o: o.to_json())
