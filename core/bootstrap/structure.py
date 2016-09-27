#!/usr/bin/env python3
"""
wooo working dir structure creation
"""

import logging
import os

from core.services.logwriter import LoggingManager
from core.parsers.config import ParseConfig


class CreateStructure():
    def __init__(self):
        LoggingManager()
        parseconfig = ParseConfig()
        self.directories = parseconfig.directories
        self.files = parseconfig.files

    def main(self):
        print("── [┬] BOOTSTRAPPING WORKING DIRS")
        self.mkdirs(self.directories)
        self.mkfiles(self.files)
        print("── [*] BOOTSTRAPPING COMPLETE")

    def mkdirs(self, directories):
        logging.debug("Directories to create: {d}".format(d=', '.join(directories)))
        for dir in directories:
            dir = (os.getcwd() + '/' + dir)
            if not os.path.exists(dir):
                os.makedirs(dir, exist_ok=True)
                logging.info("{d} created".format(d=dir))
                print("    ├─── {d}".format(d=dir))
            else:
                logging.warning("{d} already exists!".format(d=dir))
                print("   [!]── {d} already exists, skipping!".format(d=dir))

    def mkfiles(self, files):
        logging.debug("Files to create: {f}".format(f=', '.join(files)))
        for file in files:
            file = (os.getcwd() + '/' + file)
            if not os.path.exists(file):
                open(file, 'w').close()
                logging.info("{f} created".format(f=file))
                print("    ├─── {f}"
                    .format(f=file))
            else:
                logging.warning("{f} already exists, skipping!".format(f=file))
                print("   [!]── {f} already exists, skipping!"
                    .format(f=file))
