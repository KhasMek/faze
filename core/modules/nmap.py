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
            target, nmap_ports, flag, xml = self.queue.get()
            nmap = NMap()
            nmap.runnmap(target, nmap_ports, flag, xml)
            self.queue.task_done()


class NMap():
    def __init__(self):
        self.parseconfig = ParseConfig()
        self.nm = nmap.PortScanner()
        self.up_targets_dict = self.parseconfig.up_targets_dict

    def main(self):
        logging.debug("STARTING - nmap")
        target_dict = self.parseconfig.base_targets_dict
        nmap_ports = self.parseconfig.nmap_ports
        nmap_flags = self.parseconfig.nmap_flags
        nmap_threads = int(self.parseconfig.nmap_threads)
        # nmap discovery output always goes to Phase-1.
        outdir = self.parseconfig.directories[0]
        self.queuenmap(target_dict, nmap_ports, nmap_flags, nmap_threads, outdir)
        logging.debug("COMPLETED - nmap")

    def phase2(self):
        logging.debug("STARTING - nmap phase-2")
        targets = self.parseconfig.port_targets_dict
        nmap_threads = int(self.parseconfig.nmap_threads)
        outdir = self.parseconfig.nmap_phase_2_outdir
        phase_2_scripts = self.parseconfig.nmap_phase_2_scripts
        print("── [┬] RUNNING NMAP WITH PHASE-2 SCRIPTS")
        queue = Queue()
        logging.debug("Phase-2 nmap targets: {t}".format(t=targets))
        logging.debug("Phase-2 nmap scripts: {s}".format(s=phase_2_scripts))
        for x in range(nmap_threads):
            logging.debug("Nmap thread number {x}".format(x=x))
            worker = NmapWorker(queue)
            worker.daemon = True
            worker.start()
        for flag in phase_2_scripts:
            flag = "-sS -sV --script={f}".format(f=flag)
            for target, nmap_ports in targets.items():
                target = target.replace("[ ", "")
                nmap_ports = ','.join(map(str, nmap_ports))
                logging.debug("Running nmap with script - {f} on {t} : {p}"
                    .format(f=flag, t=target, p=nmap_ports))
                xml = self.parsefilename(target, outdir, flag.strip())
                queue.put((target, nmap_ports, flag, xml))
        queue.join()
        print("── [*] NMAP COMPLETE")
        logging.debug("COMPLETED - nmap phase-2")

    def parsefilename(self, target, outdir, flags):
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

    def runnmap(self, target, nmap_ports, flag, xml):
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
            # TODO: I should probably move this to targets module. ghetto 4nao
            if "Phase-2" not in str(xml):
                for host in self.nm.all_hosts():
                    self.up_targets_dict.append(host)
                self.printresults(self.nm.all_hosts())
            logging.debug(self.nm.all_hosts())
        # else: if nm. is up or something like that?
        logging.debug("XML FILENAME: {x}".format(x=xml))
        xml.write(self.nm.get_nmap_last_output())

    def queuenmap(self, target_dict, nmap_ports, nmap_flags, nmap_threads, outdir):
        print("── [┬] RUNNING NMAP AGAINST TARGETS LIST")
        queue = Queue()
        for x in range(nmap_threads):
            logging.debug("Nmap thread number {x}".format(x=x))
            worker = NmapWorker(queue)
            worker.daemon = True
            worker.start()
        for flag in nmap_flags:
            logging.debug(flag)
            for type, targets in target_dict.items():
                for target in targets:
                    logging.debug("{ty} : {ta}".format(ty=type, ta=target))
                    # TODO: this should be it's own function probably.
                    xml = self.parsefilename(target, outdir, flag.strip())
                    queue.put((target, nmap_ports, flag, xml))
        queue.join()
        print("── [*] NMAP COMPLETE")


if __name__ == "__main__":
    nmap = NMap()
    nmap.runnmap()
