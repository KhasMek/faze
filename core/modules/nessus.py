#!/usr/bin/env python3
"""
Woo nessus scanning
"""

import logging
import os

from core.parsers.config import ParseConfig
from itertools import zip_longest
from nessrest import ness6rest


class Nessus:
    def __init__(self):
        parseconfig = ParseConfig()
        self.scan_base_name = parseconfig.nessus_scan_name
        if not self.scan_base_name:
            self.scan_base_name = os.path.relpath(".", "..")
        self.url = parseconfig.nessus_url
        self.api_akey = parseconfig.nessus_api_akey
        self.api_skey = parseconfig.nessus_api_skey
        self.policy = parseconfig.nessus_policy
        self.targets = sorted(set(parseconfig.up_targets_dict))
        self.insecure = parseconfig.nessus_insecure

    def main(self):
        logging.debug("STARTING - nessus")
        logging.debug("Targets - {t}".format(t=', '.join(self.targets)))
        args = [iter(self.targets)] * 10
        # TODO: this is where the check for the home license comes in
        # We want "normal" counting for the naming.
        i = 1
        for group in zip_longest(*args):
            if len(self.targets) > 10:
                scan_name = ' '.join([self.scan_base_name, str(i)])
            else:
                scan_name = self.scan_base_name
            targets = ', '.join(map(str, (filter(None, group))))
            logging.debug("Starting Nessus on {t}".format(t=targets))
            results = self.runnessus(self.url, self.api_akey, self.api_skey,
                                     self.policy, targets, scan_name, self.insecure)
            i += 1
            # TODO: maybe make the filenames a bit more descriptive?
            xml = '/'.join([ParseConfig().directories[1], '.'
                           .join([scan_name.replace(" ", "-"), "nessus"])])
            logging.debug("Filename - {f}".format(f=xml))
            self.writeoutput(xml, results)
        print("Finished running Nessus on {t}".format(t=self.targets))
        logging.debug("COMPLETED - nessus")

    @staticmethod
    def runnessus(url, api_akey, api_skey, policy, targets, scan_name, insecure):
        scan = ness6rest.Scanner(url=url, api_akey=api_akey, api_skey=api_skey,
                                 insecure=insecure)
        scan.policy_set(name=policy)
        logging.debug("TARGETS: {t}".format(t=targets))
        scan.scan_add(targets=targets, name=scan_name)
        scan.scan_run()
        scan.scan_results()
        output = str(scan.download_scan(export_format="nessus"))
        return output

    @staticmethod
    def writeoutput(xml, results):
        with open(xml, 'a') as f:
            f.write(results)
