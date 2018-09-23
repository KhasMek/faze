#!/usr/bin/env python3
"""
Run fping on targets list
"""

import logging
import subprocess

from faze.core.helpers.term import ctact, ctinfo
from faze.core.parsers.config import ParseConfig
from faze.core.services.logwriter import LoggingManager
from textwrap import TextWrapper


class Fping:
    def __init__(self):
        LoggingManager()
        parseconfig = ParseConfig()
        self.fping_path = parseconfig.fping_path
        self.base_targets_dict = parseconfig.base_targets_dict
        self.up_targets_dict = parseconfig.up_targets_dict

    def main(self):
        logging.info("STARTING - fping")
        self.runfping(self.base_targets_dict)
        logging.info("FINISHED - fping")

    def fping(self, cmd):
        print("{i} {c}".format(i=ctinfo, c=' '.join(cmd)))
        logging.info(' '.join(cmd))
        command = subprocess.run(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL, universal_newlines=True, shell=False)
        wrapper = TextWrapper(initial_indent="{i}   ".format(i=ctinfo),
                              subsequent_indent="{i}     ".format(i=ctinfo))
        if len(command.stdout.split("\n")) > 2:
            output = wrapper.fill(command.stdout.replace("\n", ", "))
            output = output.rstrip(',')
            # TODO: write a function for this (in misc maybe) that cleans the target
            # and adds it if not a hostname (hostnames will be resolved & IP's added)
            for host in command.stdout.split("\n"):
                self.up_targets_dict.append(host)
        elif len(command.stdout.split("\n")) > 1:
            output = wrapper.fill(command.stdout.strip("\n"))
            for host in command.stdout.split("\n"):
                self.up_targets_dict.append(host)
        else:
            output = wrapper.fill("No Response")
        print(output)
        logging.info("Results: {r}".format(r=command.stdout.replace("\n", ", ")))

    def fpingsubnet(self, targets):
        for target in targets:
            t = target.split(' ')[0]
            logging.debug("SUBNET: {t}".format(t=t))
            cmd = [self.fping_path, "-g", "-a", t]
            self.fping(cmd)

    def fpingip(self, targets):
        for target in targets:
            t = target.split(' ')[0]
            logging.debug("IP: {t}".format(t=t))
            cmd = [self.fping_path, "-a", t.split('/')[0]]
            self.fping(cmd)

    def fpinghostname(self, targets):
        for target in targets:
            t = target.split(' ')[0]
            cmd = [self.fping_path, "-a", t]
            logging.debug("HOSTNAME: {t}".format(t=t))
            self.fping(cmd)

    def fpingrange(self, targets):
        for target in targets:
            t = target.split(' ')[0]
            first_three = ".".join(t.split(".")[:3])
            start_number = t.split(".")[3].split("-")[0]
            if "." in t.split("-")[1]:
                end_number = t.split("-")[1].split(".")[3]
            else:
                end_number = t.split("-")[1]
            for i in range(int(start_number), int(end_number)):
                cmd = [self.fping_path, "-a", "{ft}.{i}".format(ft=first_three, i=i)]
                self.fping(cmd)

    def runfping(self, base_targets_dict):
        print("{a} FPING".format(a=ctact))
        for _type, targets in base_targets_dict.items():
            if "subnet" in _type:
                self.fpingsubnet(targets)
            if "ip addres" in _type:
                self.fpingip(targets)
            if "hostname" in _type:
                self.fpinghostname(targets)
            if "range" in _type:
                self.fpingrange(targets)
        print("{a} FPING COMPLETE".format(a=ctact))
