#!/usr/bin/env python3
"""
Random functions hang out here until they find a real home
"""
import os
import sys

from contextlib import contextmanager


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
