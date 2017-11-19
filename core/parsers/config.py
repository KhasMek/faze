#!/usr/bin/env python3

import configparser
import json
import os
import sys

from collections import defaultdict
from core.helpers.term import ctact, cterr

config = configparser.ConfigParser()
config_file = "faze.cfg"
_loaded = ''
_rootpathcfg = os.path.join(os.path.dirname(sys.modules['__main__'].__file__),
                            config_file)
_homedircfg = os.path.join(os.path.expanduser('~'), "faze", config_file)

if _rootpathcfg:
    print("{a} LOADING CONFIG FILE - {p}".format(a=ctact, p=_rootpathcfg))
    config.read(_rootpathcfg)
    _loaded = True
if os.path.isfile(config_file):
    print("{a} LOADING CONFIG FILE - ./{p}".format(a=ctact, p=config_file))
    config.read(config_file)
    _loaded = True
if not _loaded:
    print("{e} NO CONFIG FILE FOUND! QUITTING!".format(e=cterr))
    sys.exit()


def printconfigsettings():
    print(config.sections())
    for section in config.sections():
        print(section)
        print('\n')
        for setting in config[section]:
            print(setting + " =")
            setting = config[section][setting]
            print(setting)


class ParseConfig:
    base_targets = config['DEFAULT']['base_targets']
    port_targets = config['DEFAULT']['port_targets']
    tcp_port_results = config['DEFAULT']['tcp_port_results']
    directories = json.loads(config['DEFAULT']['directories'])
    for section in config.sections():
        try:
            if config[section]["outdir"] and config[section]["enabled"]:
                # TODO: maybe logging here?
                directories.append(config[section]["outdir"])
        except KeyError:
            pass
    files = json.loads(config['DEFAULT']['files'])
    files_to_parse = []
    # This is the default list of targets as defined in the base_targets file
    base_targets_dict = defaultdict(list)
    # This is a list of up hosts to do further scanning with in nessus/qualys/etc
    up_targets_dict = []
    # This is a sec of up IP's with their open ports
    port_targets_dict = defaultdict(set)
    www_targets = {}
    fqdn_targets = []
    tld_targets = []

    # LOGGING AND MESSAGING SERVICES
    log_level = config['SERVICES']['log_level']
    log_to_file = config['SERVICES']['log_to_file']
    log_filename = config['SERVICES']['log_filename']

    # FPING
    fping_enabled = config['FPING']['enabled']
    fping_path = config['FPING']['path']

    # NMAP
    nmap_enabled = config['NMAP']['enabled']
    nmap_ports = config['NMAP']['ports']
    nmap_flags = json.loads(config['NMAP']['flags'])
    nmap_threads = config['NMAP']['threads']
    nmap_phase_2_enabled = config['NMAP']['phase_2_enabled']
    nmap_phase_2_outdir = config['NMAP']['outdir']
    nmap_phase_2_scripts = json.loads(config['NMAP']['phase_2_scripts'])

    # HTTPSCREENSHOT
    httpscreenshot_enabled = config['HTTPSCREENSHOT']['enabled']
    httpscreenshot_outdir = config['HTTPSCREENSHOT']['outdir']
    httpscreenshot_workers = config['HTTPSCREENSHOT']['workers']
    httpscreenshot_path = config['HTTPSCREENSHOT']['path']

    # NIKTO
    nikto_enabled = config['NIKTO']['enabled']
    nikto_outdir = config['NIKTO']['outdir']
    nikto_path = config['NIKTO']['path']
    nikto_filetype = config['NIKTO']['filetype']

    # DIRBRUTER
    dirbruter_enabled = config['DIRBRUTER']['enabled']
    dirbruter_outdir = config['DIRBRUTER']['outdir']
    dirbruter_wordlist_files = json.loads(config['DIRBRUTER']['wordlist_files'])
    dirbuter_ua = config['DIRBRUTER']['user_agent']

    # NESSUS
    nessus_enabled = config['NESSUS']['enabled']
    nessus_scan_name = config['NESSUS']['scan_name']
    nessus_url = config['NESSUS']['url']
    nessus_api_akey = config['NESSUS']['api_akey']
    nessus_api_skey = config['NESSUS']['api_skey']
    nessus_policy = config['NESSUS']['policy']
    nessus_insecure = config['NESSUS']['insecure']
