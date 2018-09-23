#!/usr/bin/env python3
"""
Woo nessus scanning
"""

import logging
import os
import requests
import sys
import time

from faze.core.helpers.misc import suppress_stdout
from faze.core.helpers.term import ctact, ctinfo
from faze.core.parsers.config import ParseConfig
from itertools import zip_longest
from nessrest import ness6rest
from requests.packages.urllib3.exceptions import InsecureRequestWarning


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
        print("{a} NESSUS".format(a=ctact))
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
        print("{a} NESSUS COMPLETE".format(a=ctact))
        logging.debug("COMPLETED - nessus")

    def runnessus(self, url, api_akey, api_skey, policy, targets, scan_name, insecure):
        if insecure:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        scan = ness6rest.Scanner(url=url, api_akey=api_akey, api_skey=api_skey,
                                 insecure=insecure)
        scan.policy_set(name=policy)
        logging.debug("TARGETS: {t}".format(t=targets))
        scan.scan_add(targets=targets, name=scan_name)
        scan.action(action="scans/" + str(scan.scan_id) + "/launch",
                    method="POST")
        scan.scan_uuid = scan.res["scan_uuid"]
        print("{i}   SCAN NAME: {n}".format(i=ctinfo, n=scan.scan_name))
        print("{i}   SCAN UUID: {n}".format(i=ctinfo, n=scan.scan_uuid))
        self.scanstatus(scan.tag_id, scan.scan_uuid, url, api_akey, api_skey,
                        insecure)
        with suppress_stdout():
            output = str(scan.download_scan(export_format="nessus"))
        return output

    def scanstatus(tag_id, uuid, url, api_akey, api_skey, insecure):
        running = True
        counter = 0
        scan = ness6rest.Scanner(url=url, api_akey=api_akey, api_skey=api_skey,
                                 insecure=insecure)
        print("{i}   ".format(i=ctinfo), end='')
        while running:
            scan.action(action="scans?folder_id=" + str(tag_id),
                        method="GET")
            for s in scan.res["scans"]:
                if s["uuid"] == uuid and (s['status'] == "running"
                                          or s['status'] == "pending"):
                    sys.stdout.write(".")
                    sys.stdout.flush()
                    time.sleep(2)
                    counter += 2
                    if counter % 60 == 0:
                        print("\n{i}   ".format(i=ctinfo), end='')
                if s["uuid"] == uuid and s['status'] != "running" and s['status'] != "pending":
                    running = False
                    print("\n{i}   Complete! Run time: {s} seconds."
                          .format(i=ctinfo, s=counter))

    @staticmethod
    def writeoutput(xml, results):
        with open(xml, 'a') as f:
            f.write(results)
