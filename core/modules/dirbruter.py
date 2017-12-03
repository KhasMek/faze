#!/usr/bin/env python3

import json
import logging
import requests

from core.helpers.misc import build_wordlist
from core.helpers.term import ctact, cterr, ctinfo
from core.parsers.config import ParseConfig
from core.parsers.xml import NmapXML
from core.services.logwriter import LoggingManager
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from textwrap import TextWrapper


class DirBruter:
    def __init__(self):
        LoggingManager()
        self.parseconfig = ParseConfig()
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def main(self):
        target_urls = self.parseconfig.fqdn_targets
        user_agent = self.parseconfig.dirbuter_ua
        wordlist_files = self.parseconfig.dirbruter_wordlist_files
        outdir = self.parseconfig.dirbruter_outdir
        json_output = {}
        nmapxml = NmapXML()
        nmapxml.is_fqdn()
        print("{a} RUNNING DIRBRUTER AGAINST WWW HOSTS".format(a=ctact))
        logging.info("STARTING - DirBruter")
        wrapper = TextWrapper(initial_indent="{a}   ".format(a=ctact),
                              subsequent_indent="{i}     ".format(i=ctinfo))
        print(wrapper.fill("RESOLVABLE HOSTS: {tu}".format(a=ctact, tu=", ".join(target_urls))))
        logging.debug("{a} RESOLVABLE HOSTS: {tu}".format(a=ctact, tu=target_urls))
        if target_urls:
            for target_url in target_urls:
                print("{a}   TARGET: {t}".format(a=ctact, t=target_url))
                logging.info("{a}   TARGET: {t}".format(a=ctact, t=target_url))
                if self.check_no_redirect(target_url):
                    logging.info("Building wordlist for {u}".format(u=target_url))
                    word_queue = build_wordlist(wordlist_files, 'subdirectory', "{o}/merged-dirbruter-wordlist.txt".format(o=outdir))
                    logging.info("Wordlist built")
                    json_results = self.dir_bruter(target_url, word_queue, user_agent)
                    json_output[target_url] = json_results
                else:
                    print("{i}     {t} redirects! Skipping...".format(i=ctinfo, t=target_url))
            outfile = "{od}/dirbruter_output.json".format(od=outdir)
            self.write_json_outfile(outfile, json_output)
        else:
            print("{i}     0 FQDN Hostnames found! Skipping...".format(i=ctinfo))
            logging.info("{i}     0 FQDN Hostnames found! Skipping...".format(i=ctinfo))
        print("{i} DIRBRUTER COMPLETE!".format(i=ctinfo))
        logging.info("COMPLETED - DirBruter")

    def check_no_redirect(self, url):
        request = requests.get(url, allow_redirects=False, verify=False)
        if request.status_code == 302:
            request2 = requests.get(url, allow_redirects=True, verify=False)
            # Check if it's a local redirect, or if it redirects to https/etc.
            if request2.url.split(':', 1)[0] == url.split(':', 1)[0]:
                return True
            else:
                return False
        elif request.status_code != 301:
            return True
        else:
            return False

    def dir_bruter(self, target_url, word_queue, user_agent):
        results = {}
        session = requests.Session()
        session.mount(target_url.split(':', 1)[0], HTTPAdapter(max_retries=3))
        while not word_queue.empty():
            # attempt = word_queue.get()
            attempt_list = [word_queue.get()]
            for brute in attempt_list:
                headers = {"User-Agent": user_agent}
                request = session.get(target_url + brute, headers=headers, verify=False)
                if request.status_code == 200:
                    print("{i}     [{r}] => {u}".format(i=ctinfo, r=request.status_code, u=request.url))
                    logging.info("{i}     [{r}] => {u}".format(i=ctinfo, r=request.status_code, u=request.url))
                    results[request.url] = request.status_code
                elif request.status_code != 404:
                    # TODO: add a setting `only_save_200` or something like that, if no, save these results.
                    logging.error("{e}     {c} => {u}".format(e=cterr, c=request.status_code, u=request.url))
                    pass
        return results

    def write_json_outfile(self, outfile, json_results):
        """
          "IP1":
          {
            "path1" : "response-code1",
            "path2" : "response-code2"
          },
          "IP2":
          {
            "path1" : "response-code1",
            "path2" : "response-code2"
          }
        }
        """
        with open(outfile, 'a') as outfile:
            json.dump(json_results, outfile, indent=4, sort_keys=True)
