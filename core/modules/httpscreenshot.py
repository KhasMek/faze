#!/usr/bin/env python3
"""
Calling python 2 scripts from subprocess cause I haven't written in
python3 compatibility for httpscreenshot yet.
"""

import logging
import os
import subprocess

from core.helpers.misc import ChangeDir
from core.parsers.xml import NmapXML
from core.parsers.config import ParseConfig
from core.services.logwriter import LoggingManager
from textwrap import TextWrapper

class HttpScreenshot():
    def __init__(self):
        LoggingManager()
        parseconfig = ParseConfig()
        self.www_targets = parseconfig.www_targets
        self.workers = parseconfig.httpscreenshot_workers
        self.indir = os.path.abspath(parseconfig.directories[0])
        self.outdir = os.path.abspath(parseconfig.httpscreenshot_outdir)

    def main(self):
        print("── [┬] RUNNING HTTPSCREENSHOT AGAINST WWW HOSTS")
        logging.debug("STARTING - httpscreenshot")
        self.httpscreenshotxmls(self.www_targets, self.indir,
            self.outdir, self.workers)
        print("── [*] HTTPSCREENSHOT COMPLETE!")
        logging.debug("COMPLETED - httpscreenshot")

    def httpscreenshotxmls(self, www_targets, indir, outdir, workers):
        path = ParseConfig().httpscreenshot_path
        with ChangeDir(outdir):
            for file in os.listdir(indir):
                # We want to ignore files without any port information
                if not ("-sn-" or "-sP-") in file:
                    file = os.path.join(indir, file)
                    if 'nmap' in file:
                        command = [
                            "python",
                            path,
                            "-i",
                            file,
                            "-p",
                            "-w",
                            workers,
                            "-a",
                            "-vH"
                        ]
                        # TODO: unify output with rest of program
                        # TODO: add filename output if there is an issue parsing it.
                        logging.info("Running {c}".format(c=' '.join(command)))
                        cmd = subprocess.run(command, universal_newlines=True,
                            shell=False)

