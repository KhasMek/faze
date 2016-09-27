#!/usr/bin/env python3
"""
woo testing for open tcp/udp ports
"""

# TODO: This is still pretty ghetto. Needs to be
# smarter at detecting protocol and all kinda other
# things.

import csv
import select
import socket
import string
import sys

from core.parsers.config import ParseConfig

parseconfig = ParseConfig()

class TCPPorts():
    def __init__(self):
        self.port_targets = parseconfig.port_targets
        self.tcp_port_results = parseconfig.tcp_port_results

    def main(self):
        self.parsecsv(self.port_targets)
        print("── [*] PORT TESTING COMPLETE!")

    # TODO: parsing csv's just needs to be it's own module
    def parsecsv(self, port_targets):
        with open(port_targets, 'rt') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                host = row[0]
                row.pop(0)
                ports = row
                # TODO: maybe return would be better here
                self.testtcpports(host, ports)

    def testtcpports(self, host, ports):
        results = open(self.tcp_port_results, 'a+')
        print("    ├─┬─ {h}".format(h=host))
        print("    │ └─── Protocol: TCP")
        results.write(host + '\n')
        for port in ports:
            port = int(port)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            try:
                s.connect((host, port))
                yeh = str('    │        [*] Port: ' + str(port))
                print(yeh)
                results.write(yeh + '\n')
                s.close()
            except:
                neh = str('    │        [ ] Port: ' + str(port))
                print(neh)
                results.write(neh + '\n')
                pass


if __name__ == "__main__":
    tcpports = TCPPorts()
    tcpports.main()
