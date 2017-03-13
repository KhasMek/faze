#!/usr/bin/env python3
"""
Yeah targets file parsing wooo
"""

import csv
import logging
import re
import sys

from core.parsers.config import ParseConfig
from core.parsers.xml import Xml
from core.services.logwriter import LoggingManager
from libnmap.parser import NmapParser
from textwrap import TextWrapper

parseconfig = ParseConfig()

class BaseTargetsFile():
    def __init__(self):
        LoggingManager()
        self.base_targets = parseconfig.base_targets
        self.base_targets_dict = parseconfig.base_targets_dict

    def main(self):
        print("── [┬] SORTING TARGETS BY TYPE")
        self.parsebasetargets(self.base_targets)
        for k, v in sorted(self.base_targets_dict.items()):
            wrapper = TextWrapper(initial_indent="", subsequent_indent="    │\t\t\t")
            # TODO: format output to match fping
            print("    ├─── {ty} \t{ta}"
                .format(ty=k.upper() + ":", ta=wrapper.fill(", ".join(v))))
            logging.info("{k}: {v}".format(k=k, v=', '.join(v)))
        print("── [*] SORTING COMPLETE")

    def addtarget(self, type, defined_target):
        self.base_targets_dict[type].append(defined_target)
        logging.debug("{ty}: {ta}".format(ty=type, ta=defined_target))

    def targettype(self, target):
        logging.debug("target = {t}".format(t=target))
        t = target
        if '--' in t:
            split = t.split(' ')
            t = split[0]
            logging.debug("t = {t}".format(t=t))
        # Assume we're not dealing with IPv6 address space
        if re.search('[a-zA-Z]', t):
            self.addtarget('hostname', target)
            logging.debug("HOSTNAME: {t}".format(t=target))
        elif "-" in t:
            self.addtarget('range', target)
            logging.debug("RANGE: {t}".format(t=target))
        elif re.search('^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', t):
            self.addtarget('ip address', target)
            logging.debug("IP: {t}".format(t=target))
        elif "/32" in t:
            self.addtarget('ip address', target)
            logging.debug("IP: {t}".format(t=target))
        elif re.search('/[0-9]{1,2}', t):
            self.addtarget('subnet', target)
            logging.debug("SUBNET: {t}".format(t=target))
        else:
            print("── [!] UNKNOWN: {t}".format(t=target))
            logging.warning("{t} is an unknown IP type!".format(t=target))

    def parsebasetargets(self, base_targets):
        try:
            for line in open(base_targets):
                if line.strip(' \n'):
                    # Nuke whitespace
                    target = re.sub('[\s+]', '', line)
                    # Account for exclusions (not exclude files). Getto but easy.
                    if '--' in target:
                        target = re.sub("--exclude", " --exclude ", target)
                    self.targettype(target)
                    logging.debug(target)
        except FileNotFoundError:
            print(("── [!] TARGETS FILE ({bt}) NOT FOUND!".format(bt=base_targets)))
            logging.error("TARGETS FILE NOT FOUND!!! QUITTING!!!")
            sys.exit("── [!] QUITTING!")


# TODO: - Add support for Qualys/Nessus xml's
#       - Break into modules for parsing different xml's and writing csv's
#       - Check TCP/UDP ports separately
class PortTargetsFile():
    def __init__(self):
        LoggingManager()
        self.files_to_parse = parseconfig.files_to_parse
        self.port_targets = parseconfig.port_targets
        self.port_targets_dict = parseconfig.port_targets_dict
        self.phase1 = parseconfig.directories[0]

    def main(self):
        print("── [┬] SORTING UP TARGETS WITH OPEN PORTS")
        xml = Xml()
        xml.validatenmapxml(self.phase1)
        self.parsehosts(self.files_to_parse)
        self.writecsv(self.port_targets)

    def parsehosts(self, files_to_parse):
        for xml in files_to_parse:
            logging.info("Parsing {x}".format(x=xml))
            infile = NmapParser.parse_fromfile(xml)
            for host in infile.hosts:
                if host.services:
                    address = host.address
                    for s in host.services:
                        if s.state != 'closed':
                            self.port_targets_dict[host.address].add(s.port)
                logging.info("{h}: {s}".format(h=host, s=host.services))

    def writecsv(self, port_targets):
        with open(port_targets, 'w') as outfile:
            writer = csv.writer(outfile)
            for k,v in self.port_targets_dict.items():
                v= list(v)
                writer.writerow([k] + v)
