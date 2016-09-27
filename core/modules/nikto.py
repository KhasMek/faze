#!/usr/bin/env python3
"""
woo nikto scanning
"""

import os
import logging
import subprocess

from core.parsers.xml import NmapXML
from core.parsers.config import ParseConfig
from core.services.logwriter import LoggingManager

class Nikto():
    def __init__(self):
        parseconfig = ParseConfig()
        self.www_targets = parseconfig.www_targets
        self.nikto_path = parseconfig.nikto_path
        self.outdir = parseconfig.nikto_outdir
        self.filetype = parseconfig.nikto_filetype

    def main(self):
        print("── [┬] RUNNING NIKTO AGAINST WEB HOSTS")
        logging.debug("STARTING - nikto")
        self.runnikto(self.www_targets, self.outdir, self.nikto_path, self.filetype)
        print("── [*] NIKTO COMPLETE")
        logging.debug("COMPLETED - nikto")

    def runnikto(self, www_targets, outdir, nikto_path, filetype):
        nmapxml = NmapXML()
        nmapxml.wwwports()
        for k,v in www_targets.items():
            host = k
            port = v[0]
            service = v[1]
            outfile = str("{o}/nikto-{p}-{h}.txt"
                        .format(o=outdir, p=port, h=host))
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
            print("    ├─┬─ TARGET: {h}:{p} ({s})"
                    .format(h=host, p=port, s=service))
            print("    │ ├─── {c}".format(c=' '.join(command)))
            # TODO: This needs a try and except for FileNotFoundError
            logging.info("Running {c}".format(c=' '.join(command)))
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=None,
                shell=False)
            print("    │ └─ COMPLETE: {h}:{p}".format(h=host, p=port))
