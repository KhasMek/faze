#!/usr/bin/env python3
"""
wooo module for writing logs
"""

import logging
import os

from core.parsers.config import ParseConfig


parseconfig = ParseConfig()

class LoggingManager():
    def __init__(self):
        log_level = parseconfig.log_level
        # TODO: I don't know if this check actually disables it
        if parseconfig.log_to_file:
            LogToFile(log_level)

class LogToFile():
    def __init__(self, log_level):
        log_filename = parseconfig.log_filename
        if not os.path.isfile(log_filename):
            print("── [*] CREATING LOGFILE")
            try:
                os.makedirs(os.path.dirname(parseconfig.log_filename), exist_ok=True)
            # Log file will be created in cwd.
            except FileNotFoundError:
                pass
        logging.basicConfig(format='[%(levelname)s]\t (%(asctime)s): %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S %z', filename=log_filename, level=log_level)

    def main(self, severity, data):
        pass
