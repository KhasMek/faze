#!/usr/bin/env python3
"""
Random functions hang out here until they find a real home
"""
import os


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
