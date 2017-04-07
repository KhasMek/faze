#!/usr/bin/env python3
"""
wooo working dir structure creation
"""

import logging
import os

from core.services.logwriter import LoggingManager
from core.parsers.config import ParseConfig


class CreateStructure:
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

    @staticmethod
    def mkdirs(directories):
        logging.debug("Directories to create: {d}".format(d=', '.join(directories)))
        for _dir in directories:
            _dir = (os.getcwd() + '/' + _dir)
            if not os.path.exists(_dir):
                os.makedirs(_dir, exist_ok=True)
                logging.info("{d} created".format(d=_dir))
                print("    ├─── {d}".format(d=_dir))
            else:
                logging.warning("{d} already exists!".format(d=_dir))
                print("   [!]── {d} already exists, skipping!".format(d=_dir))

    @staticmethod
    def mkfiles(files):
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
