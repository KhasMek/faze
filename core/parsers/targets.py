#!/usr/bin/env python3
"""
Yeah targets file parsing wooo
"""

import csv
import logging
import re
import sys
import tldextract

from core.helpers.term import ctact, cterr, ctinfo
from core.parsers.config import ParseConfig
from core.parsers.xml import Xml
from core.services.logwriter import LoggingManager
from libnmap.parser import NmapParser
from textwrap import TextWrapper

parseconfig = ParseConfig()


class BaseTargetsFile:
    def __init__(self):
        LoggingManager()
        self.base_targets = parseconfig.base_targets
        self.base_targets_dict = parseconfig.base_targets_dict

    def main(self):
        print("{a} SORTING TARGETS BY TYPE".format(a=ctact))
        self.parsebasetargets(self.base_targets)
        for k, v in sorted(self.base_targets_dict.items()):
            wrapper = TextWrapper(initial_indent="", subsequent_indent="    │\t\t\t")
            # TODO: format output to match fping
            print("{i}   {ty} \t{ta}"
                  .format(i=ctinfo, ty=k.upper() + ":", ta=wrapper.fill(", ".join(v))))
            logging.info("{k}: {v}".format(k=k, v=', '.join(v)))
        print("{i} SORTING COMPLETE".format(i=ctinfo))

    def addtarget(self, _type, defined_target):
        self.base_targets_dict[_type].append(defined_target)
        logging.debug("{ty}: {ta}".format(ty=_type, ta=defined_target))

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
        elif re.search('^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                       t):
            self.addtarget('ip address', target)
            logging.debug("IP: {t}".format(t=target))
        elif "/32" in t:
            self.addtarget('ip address', target)
            logging.debug("IP: {t}".format(t=target))
        elif re.search('/[0-9]{1,2}', t):
            self.addtarget('subnet', target)
            logging.debug("SUBNET: {t}".format(t=target))
        else:
            print("{e} UNKNOWN: {t}".format(e=cterr, t=target))
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
            print(("{e} TARGETS FILE ({bt}) NOT FOUND!".format(e=cterr, bt=base_targets)))
            logging.error("TARGETS FILE NOT FOUND!!! QUITTING!!!")
            sys.exit("{e} QUITTING!".format(e=cterr))

    def parse_tlds(self):
        tld_targets = parseconfig.tld_targets
        www_targets = parseconfig.www_targets
        if 'hostname' in self.base_targets_dict:
            for hostname in self.base_targets_dict['hostname']:
                breakdown = tldextract.extract(hostname)
                tld_targets.append(breakdown.registered_domain)
        if len(www_targets) > 0:
            for hostname in www_targets:
                breakdown = tldextract.extract(hostname)
                tld_targets.append(breakdown.registered_domain)


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
        print("{i} SORTING UP TARGETS WITH OPEN PORTS".format(i=ctinfo))
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
                    for s in host.services:
                        if s.state != 'closed':
                            self.port_targets_dict[host.address].add(s.port)
                logging.info("{h}: {s}".format(h=host, s=host.services))

    def writecsv(self, port_targets):
        with open(port_targets, 'w') as outfile:
            writer = csv.writer(outfile)
            for k, v in self.port_targets_dict.items():
                v = list(v)
                writer.writerow([k] + v)
