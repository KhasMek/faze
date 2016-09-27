#!/usr/bin/env python3
"""
wooo run nmap and stuffs
"""

import argparse
import ipaddress
import logging
import nmap
import os

from core.parsers.config import ParseConfig
from core.services.logwriter import LoggingManager
from queue import Queue
from threading import Thread
from time import strftime


class NmapWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            target, nmap_ports, flag = self.queue.get()
            nmap = NMap()
            nmap.runnmap(target, nmap_ports, flag)
            self.queue.task_done()


class NMap():
    def __init__(self):
        # Keep an eye on this - may cause issues
        parseconfig = ParseConfig()
        self.nmap_ports = parseconfig.nmap_ports
        self.nmap_flags = parseconfig.nmap_flags
        self.nmap_threads = int(parseconfig.nmap_threads)
        self.outdir = parseconfig.directories[0]
        self.nm = nmap.PortScanner()
        self.base_targets_dict = parseconfig.base_targets_dict
        self.up_targets_dict = parseconfig.up_targets_dict

    def main(self):
        logging.debug("STARTING - nmap")
        self.queuenmap(self.nmap_ports, self.nmap_flags, self.nmap_threads)
        logging.debug("COMPLETED - nmap")

    def parsefilename(self, target, outdir, flags):
        # TODO: account for --script=$script and --script=subdir/$script
        t = target
        logging.debug("Parsing {t}".format(t=t))
        if "--" in t:
            split = t.split(' ')
            t = split[0]
        if "/" in t:
            ending = ipaddress.ip_network(t, strict=False).network_address
        else:
            ending = t
        for char in [ "=", "/", "--", "." ]:
            if char in flags:
                flags = flags.replace(char, "_")
        f = str("{o}/nmap{f}-{e}.xml"
                .format(o=outdir, f=flags.replace(" ", ""), e=ending))
        xml = open(f, 'a')
        logging.debug("Filename for {t} - {f}".format(t=t, f=f))
        return xml

    def printresults(self, results):
        logging.debug("{r}".format(r=results))
        print("    ├─┬─ {c}".format(c=self.nm.command_line()))
        for host in results:
            print("    │ ├─┬─ Host: {h} ({hn})"
                .format(h=host, hn=self.nm[host].hostname()))
            print("    │ │ └─── State: {s}".format(s=self.nm[host].state()))
            for proto in self.nm[host].all_protocols():
                print("    │ │        Protocol: {p}".format(p=proto.upper()))
                ports = sorted(self.nm[host][proto].keys())
                for port in ports:
                    print("    │ │          {p}\t{n}"
                        .format(p=port, n=self.nm[host][proto][port]['name']))
        print("    │ └─ COMPLETE!")

    def runnmap(self, target, nmap_ports, flag):
        # -sP may output a different json format?
        logging.debug("{t} {p} {f}".format(t=target, p=nmap_ports, f=flag))
        if [variable for variable in flag.split() if "-sP" in variable]:
            print("    ├── nmap {f} {t}"
                .format(f=flag, t=target))
            logging.info("Running nmap on {t} with flags '{f}'"
                .format(t=target, f=flag))
            self.nm.scan(hosts=target, arguments=flag)
            # Check if nmap commands need root/sudo.
        elif [variable for variable in flag.split() if ("-sF" or "-sU") in variable]:
            print("    ├── nmap {f} {t}"
                .format(f=flag, t=target))
            logging.info("Running nmap on {t} with flags '{f}'"
                .format(t=target, f=flag))
            self.nm.scan(hosts=target, arguments=flag, sudo=True)
        else:
            print("    ├── nmap {f} {t} {p}"
                .format(f=flag, t=target, p=nmap_ports))
            logging.info("Running nmap on {t} with flags '{f}'"
                .format(t=target, f=flag))
            self.nm.scan(hosts=target, arguments=flag, ports=nmap_ports)
        logging.debug("HOSTS: {h}".format(h=self.nm.all_hosts()))
        if self.nm.all_hosts():
            # We may be able to just feed them all in at once?
            for host in self.nm.all_hosts():
                self.up_targets_dict.append(host)
            self.printresults(self.nm.all_hosts())
            logging.debug(self.nm.all_hosts())
        # else: if nm. is up or something like that?
        # TODO: this should be it's own function probably.
        xml = self.parsefilename(target, self.outdir, flag.strip())
        logging.debug("XML FILENAME: {x}".format(x=xml))
        xml.write(self.nm.get_nmap_last_output())

    def queuenmap(self, nmap_ports, nmap_flags, nmap_threads):
        print("── [┬] RUNNING NMAP AGAINST TARGETS LIST")
        queue = Queue()
        for x in range(nmap_threads):
            logging.debug("Nmap thread number {x}".format(x=x))
            worker = NmapWorker(queue)
            worker.daemon = True
            worker.start()
        for flag in self.nmap_flags:
            logging.debug(flag)
            for type, targets in self.base_targets_dict.items():
                for target in targets:
                    logging.debug("{ty} : {ta}".format(ty=type, ta=target))
                    queue.put((target, self.nmap_ports, flag))
        queue.join()
        print("── [*] NMAP COMPLETE")


if __name__ == "__main__":
    nmap = NMap()
    nmap.runnmap()
