#!/usr/bin/env python3
"""
wooo xml parsing
"""

import os
import logging
import xml.etree.ElementTree as ET

from core.helpers.term import cterr
from core.helpers.misc import ResolveHostname
from core.parsers.config import ParseConfig
from libnmap.parser import NmapParser
from xml.etree.ElementTree import ParseError


# TODO: This could probably be smarter.
# xml file detection.
class Xml:
    @staticmethod
    def validatenmapxml(phase1):
        for file in os.listdir(phase1):
            file = os.path.join(phase1, file)
            files_to_parse = ParseConfig().files_to_parse
            try:
                ET.parse(file)
                logging.debug("Adding {f} to list of files to parse"
                              .format(f=file))
                files_to_parse.append(file)
            except ParseError:
                logging.warning("{f} is malformed or not an xml".format(f=file))
                print("{e} {f} is malformed or not an xml".format(e=cterr, f=file))
                pass
            except IOError:
                # File is a directory.
                pass
        return files_to_parse


class NmapXML:
    @staticmethod
    def wwwports():
        files_to_parse = ParseConfig().files_to_parse
        www_targets = ParseConfig().www_targets
        for xml in files_to_parse:
            infile = NmapParser.parse_fromfile(xml)
            for host in infile.hosts:
                if host.services:
                    address = host.address
                    for s in host.services:
                        if "http" in s.service:
                            www_targets[address] = s.port, s.service
                            logging.debug("{a}:{p}".format(a=address, p=s.port))

    @staticmethod
    def is_fqdn():
        files_to_parse = ParseConfig().files_to_parse
        fqdn_targets = ParseConfig().fqdn_targets
        for xml in files_to_parse:
            infile = NmapParser.parse_fromfile(xml)
            for host in infile.hosts:
                if host.hostnames:
                    for domain in host.hostnames:
                        fqdn = ResolveHostname.resolve(domain)
                        if fqdn:
                            for s in host.services:
                                if "https" in s.service:
                                    fqdn_targets.append('https://' + domain)
                                if "http" in s.service:
                                    if "ssl" in s.tunnel:
                                        fqdn_targets.append('https://' + domain)
                                    else:
                                        fqdn_targets.append('http://' + domain)
