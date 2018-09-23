#!/usr/bin/env python3

import datetime
import logging
import os
import re
import subprocess

from faze.core.parsers.config import ParseConfig
from faze.core.parsers.targets import BaseTargetsFile
from faze.core.helpers.misc import build_wordlist, ResolveHostname
from faze.core.helpers.term import clean_output, ctact, cterr, ctinfo
from faze.core.services.logwriter import LoggingManager
from faze.core.services.threading import FazeWorker
from queue import Queue


LoggingManager()
parseconfig = ParseConfig()


class SubBruter:
    def main(self):
        bts = BaseTargetsFile()
        bts.parse_tlds()
        wordlist_files = parseconfig.subbruter_domain_wordlists
        outdir = parseconfig.subbruter_outdir
        threads = parseconfig.subbruter_threads
        tld_targets = str(','.join(parseconfig.tld_targets))
        logging.info("Top Level Domains: {tt}".format(tt=tld_targets))
        merged_wordlist = "{o}/merged-subbruter-wordlist.txt".format(o=outdir)
        build_wordlist(wordlist_files, 'subdomain', merged_wordlist)
        brutefore_subdomains = parseconfig.subbruter_bruteforce_dns_enabled
        print("{a} RUNNING SUBBRUTER AGAINST WWW HOSTS".format(a=ctact))
        if tld_targets:
            outfiles = self.run_busters(tld_targets, merged_wordlist, outdir, threads, brutefore_subdomains)
            # Wait for these three programs to finish running before combining all the results and kicking off altdns
            merged_results = self.combine_results(outdir, outfiles)
            resolvable_wordlist = "{o}/merged-resolvable-wordlist.txt".format(o=outdir)
            with open(merged_results, 'r') as f:
                with open(resolvable_wordlist, 'w') as f1:
                    for line in f:
                        logging.debug("attempt: {w}".format(w=line.rstrip()))
                        if ResolveHostname.resolve(line.rstrip()):
                            logging.debug("resolvable: {w}".format(w=line.rstrip()))
                            f1.write(line)
                        else:
                            logging.debug("not resolvable: {w}".format(w=line.rstrip()))
                logging.info("All resolvable subdomains added to {rw}".format(rw=resolvable_wordlist))
            # Run altdns on merged, resolvable results, if any.
            if os.path.exists(resolvable_wordlist):
                altdns_path = parseconfig.subbruter_altdns_path
                permutated_domains_file = "{o}/altdns-permutations.txt".format(o=outdir)
                altdns_outfile = "{o}/altdns-results.txt".format(o=outdir)
                AltDns(resolvable_wordlist, altdns_outfile, altdns_path,
                       altered_subdomains_file=permutated_domains_file, threads=threads)
                subbruter_outfile = "{o}/SubBruter-final-results.txt".format(o=outdir)
                with open(subbruter_outfile, 'w') as outfile:
                    for file in [resolvable_wordlist, altdns_outfile]:
                        with open(file, 'r') as infile:
                            for line in infile:
                                outfile.write(line)
                                if parseconfig.subbruter_add_discovered_domains:
                                    logging.debug("Adding {d} to base_targets_dict".format(d=line.rstrip()))
                                    bts.addtarget('hostname', line.rstrip())
                print("{i} FINAL RESULTS - {f}".format(i=ctinfo, f=subbruter_outfile))
                logging.debug("FINAL RESULTS - {f}".format(f=subbruter_outfile))
            else:
                print("{e}   NO RESOLVABLE DOMAINS FOUND!!!".format(e=cterr))
                logging.debug("NO RESOLVABLE DOMAINS FOUND!!!")
        else:
            print("{i}   0 Domains found! Skipping...".format(i=ctinfo))
            logging.debug("Zero (0) FQDN Hostnames found! Skipping...")
        print("{i} SUBBRUTER COMPLETE!".format(i=ctinfo))
        logging.info("COMPLETED - DirBruter")

    def run_busters(self, tld_targets, merged_wordlist, outdir, threads, brutefore_subdomains=''):
        outfiles = {}
        queue = Queue()
        for x in range(3):
            worker = FazeWorker(queue)
            worker.daemon = True
            worker.start()
        gobuster_outfile = "{o}/gobuster-results.txt".format(o=outdir)
        gobuster_path = parseconfig.subbruter_gobuster_path
        if gobuster_path:
            queue.put(lambda: GoBuster(tld_targets, merged_wordlist, gobuster_outfile, threads=threads,
                                       gobuster_path=gobuster_path))
            outfiles['GoBuster'] = gobuster_outfile
        reconng_path = parseconfig.subbruter_reconng_path
        if reconng_path:
            queue.put(lambda: EnumAll(tld_targets, merged_wordlist, outdir, reconng_path=reconng_path,
                                      bruteforce=brutefore_subdomains))
            outfiles['enumall'] = "{o}/enumall-results.csv".format(o=outdir)
        sublister_outfile = "{o}/sublister-results.txt".format(o=outdir)
        sublister_path = parseconfig.subbruter_sublister_path
        if sublister_path:
            queue.put(lambda: Sublist3r(tld_targets, merged_wordlist, sublister_outfile, threads=threads,
                                        sublister_path=sublister_path, bruteforce=brutefore_subdomains))
            outfiles['Sublist3r'] = sublister_outfile
        queue.join()

        return outfiles

    def combine_results(self, outdir, outfiles):
        logging.info("combining results of {of} to {od}".format(of=outfiles, od=outdir))
        if 'enumall' in outfiles:
            logging.debug("enumall found in outfiles")
            enumall_clean_file = "{o}/enumall-results.txt".format(o=outdir)
            with open(outfiles['enumall'], 'r') as f:
                dirty_lines = f.readlines()
                with open(enumall_clean_file, 'w') as f1:
                    for line in dirty_lines:
                        clean_line = line.split(',', 1)[0].replace('"', '').lower()
                        f1.write("{c}\n".format(c=clean_line))
                        outfiles['enumall'] = enumall_clean_file
        if 'GoBuster' in outfiles:
            logging.debug("gobuster found in outfiles")
            gobuster_clean_file = outfiles['GoBuster']
            with open(outfiles['GoBuster'], 'r') as f:
                dirty_lines = f.readlines()
                with open(gobuster_clean_file, 'w') as f1:
                    for line in dirty_lines:
                        clean_line = line.split(' ', 1)[1].lower()
                        f1.write("{c}".format(c=clean_line))
                        outfiles['GoBuster'] = gobuster_clean_file
        merged_results = "{o}/merged-results.txt".format(o=outdir)
        build_wordlist(outfiles.values(), 'subdomain', merged_results)
        logging.info("results combined and written to {mr}".format(mr=merged_results))

        return merged_results


class GoBuster:
    def __init__(self, tld_targets, wordlist, outfile, threads='20', gobuster_path=""):
        print("{i}   STARTING - GoBuster".format(i=ctinfo))
        logging.info("STARTING - GoBuster")
        for target in tld_targets.split(','):
            cmd = [
                gobuster_path,
                '-m',
                'dns',
                '-u',
                target,
                '-w',
                wordlist,
                '-t',
                threads,
                '-fw',
                '-o',
                outfile
            ]
            logging.debug("running GoBuster with command {cmd}".format(cmd=cmd))
            command = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=None, universal_newlines=True, shell=False)
            if command.stdout:
                print("{i}   GoBuster Results for {t}:".format(i=ctinfo, t=target))
                for line in command.stdout.split("\n"):
                    if line.startswith("Found: "):
                        print("{i}     {o}".format(i=ctinfo, o=line[7:]))
        print("{i}   COMPLETED - GoBuster".format(i=ctinfo))
        logging.info("COMPLETED - GoBuster")


class EnumAll:
    def __init__(self, tld_targets, wordlist, outdir, reconng_path="", bruteforce=""):
        """
        Full credit to jhaddix (https://github.com/jhaddix/domain) for this name/concept/method.
        Currently this just writes a resource file and invokes recon-ng through subprocess.run
        because some people just insist on only supporting python2.
        """
        workspace = "faze-" + datetime.datetime.now().strftime('%M-%H-%m_%d_%Y')
        resource_file = str("{o}/{w}.resource".format(o=outdir, w=workspace))
        module_list = ["recon/domains-hosts/bing_domain_web", "recon/domains-hosts/google_site_web",
                       "recon/domains-hosts/netcraft", "recon/domains-hosts/shodan_hostname",
                       "recon/netblocks-companies/whois_orgs", "recon/hosts-hosts/resolve"]
        bruteforce_module_list = ["recon/domains-hosts/brute_hosts"]
        print("{i}   STARTING - EnumAll".format(i=ctinfo))
        logging.info("STARTING - EnumAll")

        with open(resource_file, 'w') as f:
            f.write("workspaces select {w}\n".format(w=workspace))
            for _module in module_list:
                f.write("use {m}\n".format(m=_module))
                f.write("set SOURCE {t}\n".format(t=tld_targets))
                f.write("run\n")
            if bruteforce:
                for _module in bruteforce_module_list:
                    f.write("use {m}\n".format(m=_module))
                    f.write("set WORDLIST {w}\n".format(w=wordlist))
                    f.write("set SOURCE {t}\n".format(t=tld_targets))
                    f.write("run\n")
            f.write("use reporting/csv\n")
            f.write("set FILENAME {o}/enumall-results.csv\n".format(o=outdir))
            f.write("run\n")
            f.write("exit\n")

        cmd = [
            "python2",
            reconng_path,
            "--no-check",
            "-r",
            resource_file
        ]
        logging.debug("running EnumAll with command {cmd}".format(cmd=cmd))
        command = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=None, universal_newlines=True, shell=False)
        if command.stdout:
            print("{i}   EnumAll Results:".format(i=ctinfo))
            for line in command.stdout.split("\n"):
                line = clean_output(line)
                if line.startswith("[*] [host] ") and "No record found." not in line:
                    print("{i}     {o}".format(i=ctinfo, o=line[11:]))
                elif line.startswith("[*]") and "=> (" in line:
                    print("{i}     {o}".format(i=ctinfo, o=line[4:]))
        print("{i}   COMPLETED - EnumAll!".format(i=ctinfo))
        logging.info("COMPLETED - EnumAll!")


class Sublist3r:
    """
    It would be a lot cleaner to invoke sublist3r as native python code, but I think until it becomes part of pip,
    or at least has a setup.py file, we'll just call it like plebs
    """
    def __init__(self, tld_targets, merged_wordlist, sublister_outfile, threads='20', sublister_path="", bruteforce=""):
        if bruteforce:
            print("{e}     Bruteforce is currently disabled for Sublist3r, but it will be available in the future."
                  .format(e=cterr))
        print("{i}   STARTING - Sublist3r".format(i=ctinfo))
        logging.info("STARTING - Sublist3r")
        for target in tld_targets.split(','):
            cmd = [
                "python",
                sublister_path,
                "-d",
                target,
                "-t",
                threads,
                "-o",
                sublister_outfile
            ]
            logging.debug("running Sublist3r with command {cmd}".format(cmd=cmd))
            command = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=None, universal_newlines=True, shell=False)
            if command.stdout:
                print("{i}   Sublist3r Results for {t}:".format(i=ctinfo, t=target))
                for line in command.stdout.split("\n"):
                    line = clean_output(line)
                    if re.match('[A-Za-z]', line):
                        print("{i}     {o}".format(i=ctinfo, o=line))
        print("{i}   COMPLETED - Sublist3r".format(i=ctinfo))
        logging.info("COMPLETED - Sublist3r")


class AltDns:
    def __init__(self, input_file, output_file, altdns_path="", dns_server="8.8.8.8",
                 altered_subdomains_file="altdns-permutations.txt", threads='20'):
        permutations_list = "{p}/words.txt".format(p=os.path.dirname(altdns_path))
        print("{i}   STARTING - AltDNS".format(i=ctinfo))
        logging.info("STARTING - AltDNS")
        cmd = [
            "python2",
            altdns_path,
            "-i",
            input_file,
            "-o",
            altered_subdomains_file,
            "-w",
            permutations_list,
            "-r",
            "-e",
            "-d",
            dns_server,
            "-s",
            output_file,
            "-t",
            threads
        ]
        logging.debug("running AltDNS with command {cmd}".format(cmd=cmd))
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=None, universal_newlines=True, shell=False)
        print("{i}   COMPLETED - AltDNS".format(i=ctinfo))
        logging.info("COMPLETED - AltDNS")