#!/usr/bin/env python3
"""
Random functions hang out here until they find a real home
"""
import logging
import os
import socket
import sys

from contextlib import contextmanager
from multiprocessing import Queue


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


class ChangeDir:
    """
    Context manager for changing the current working directory
    """
    def __init__(self, newpath):
        self.newpath = os.path.expanduser(newpath)

    def __enter__(self):
        self.savedpath = os.getcwd()
        os.chdir(self.newpath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedpath)


class ResolveHostname:
    """
    Check if hostname is resolvable or not

    from core.helpers.misc import ResolveHostname
    resolve = ResolveHostname.resolve
    resolve("google.com")
    """
    @staticmethod
    def resolve(hostname):
        try:
            socket.gethostbyname(hostname)
            return True
        except socket.error:
            return


def build_wordlist(wordlist_files, kind=None, outfile=None):
    """
    Merge, sort and drop duplicates into a master wordlist file
    and write to disk if requested.
    :param wordlist_files:
    :param kind:
    :param outfile:
    :return:
    """
    raw_words = set()
    logging.debug("Building wordlist with files - {wl} with kind set to - {k} to outfile - {o}"
                  .format(wl=wordlist_files, k=kind, o=outfile))
    for wordlist in wordlist_files:
        with open(wordlist, 'r') as f:
            for line in f.readlines():
                word = line.rstrip()
                if kind is "subdirectory":
                    # Let's prepend / right off the bat if it's not already there.
                    if not word.startswith('/'):
                        word = "/{w}".format(w=word)
                    # Assume it's a directory (or API endpoint) if no file extension.
                    if '.' not in word and not word.endswith('/'):
                        word = "{w}/".format(w=word)
                raw_words.add(word)
    if logging.getLogger().getEffectiveLevel() == logging.DEBUG and outfile or kind is "subdomain":
        with open(outfile, 'w') as f:
            for word in raw_words:
                f.write("{w}\n".format(w=word))
    words = Queue()
    if kind is not "subdomain":
        for word in raw_words:
            logging.debug("Adding {w} to wordlist".format(w=word))
            words.put(word)
        return words
