#!/usr/bin/env python3
"""
woo nikto scanning
"""

import logging
import subprocess

from core.helpers.term import ctact, ctinfo
from core.parsers.xml import NmapXML
from core.parsers.config import ParseConfig


class Nikto:
    def __init__(self):
        parseconfig = ParseConfig()
        self.www_targets = parseconfig.www_targets
        self.nikto_path = parseconfig.nikto_path
        self.outdir = parseconfig.nikto_outdir
        self.filetype = parseconfig.nikto_filetype

    def main(self):
        print("{a} RUNNING NIKTO AGAINST WEB HOSTS".format(a=ctact))
        logging.debug("STARTING - nikto")
        self.runnikto(self.www_targets, self.outdir, self.nikto_path, self.filetype)
        print("{i} NIKTO COMPLETE".format(i=ctinfo))
        logging.debug("COMPLETED - nikto")

    @staticmethod
    def runnikto(www_targets, outdir, nikto_path, filetype):
        nmapxml = NmapXML()
        nmapxml.wwwports()
        for k, v in www_targets.items():
            host = k
            port = v[0]
            service = v[1]
            outfile = str("{o}/nikto-{p}-{h}.{f}"
                          .format(o=outdir, p=port, h=host, f=filetype))
            command = [
                nikto_path,
                "-h",
                host,
                "-p",
                str(port),
                "-output",
                outfile,
                "-Format",
                filetype
            ]
            print("{i}   TARGET: {h}:{p} ({s})"
                  .format(i=ctinfo, h=host, p=port, s=service))
            print("{i}     {c}".format(i=ctinfo, c=' '.join(command)))
            # TODO: This needs a try and except for FileNotFoundError
            logging.info("Running {c}".format(c=' '.join(command)))
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=None,
                           shell=False)
            print("{i}   COMPLETE: {h}:{p}".format(i=ctinfo, h=host, p=port))
