#!/usr/bin/env python3
"""
Calling python 2 scripts from subprocess cause I haven't written in
python3 compatibility for httpscreenshot yet.
"""

import logging
import os
import subprocess

from core.helpers.misc import ChangeDir
from core.helpers.term import ctact, cterr, ctinfo
from core.parsers.config import ParseConfig
from core.services.logwriter import LoggingManager


class HttpScreenshot:
    def __init__(self):
        LoggingManager()
        parseconfig = ParseConfig()
        self.www_targets = parseconfig.www_targets
        self.workers = parseconfig.httpscreenshot_workers
        self.indir = os.path.abspath(parseconfig.directories[0])
        self.outdir = os.path.abspath(parseconfig.httpscreenshot_outdir)

    def main(self):
        print("{a} RUNNING HTTPSCREENSHOT AGAINST WWW HOSTS".format(a=ctact))
        logging.debug("STARTING - httpscreenshot")
        self.httpscreenshotxmls(self.indir,
                                self.outdir, self.workers)
        print("{i} HTTPSCREENSHOT COMPLETE!".format(i=ctinfo))
        logging.debug("COMPLETED - httpscreenshot")

    @staticmethod
    def httpscreenshotxmls(indir, outdir, workers):
        path = ParseConfig().httpscreenshot_path
        with ChangeDir(outdir):
            for file in os.listdir(indir):
                # We want to ignore files without any port information
                if not ("-sn-" or "-sP-") in file:
                    file = os.path.join(indir, file)
                    if 'nmap' in file:
                        cmd = [
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
                        logging.info("Running {c}".format(c=' '.join(cmd)))
                        command = subprocess.run(cmd, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE, universal_newlines=True, shell=False)
                        if command.stdout:
                            for line in command.stdout[:-1].split("\n"):
                                print("{i} {l}".format(i=ctinfo, l=line.split(' ', 1)[-1]))
                        if command.stderr:
                            print("{e} Error reading {f}".format(e=cterr, f=file))
                            for line in command.stderr[:-1].split("\n"):
                                print("{i} {l}".format(i=cterr, l=line.split(' ', 1)[-1]))
