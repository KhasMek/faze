#!/usr/bin/env python3
"""
Consolidated area for terminal formatters.
"""
import re

from colorama import Fore, Style


ctact = str(Fore.GREEN + Style.DIM + '[+]' + Style.RESET_ALL)
cterr = str(Fore.RED + Style.DIM + '[-]' + Style.RESET_ALL)
ctinfo = str(Fore.BLUE + Style.DIM + '[*]' + Style.RESET_ALL)


def clean_output(input):
    output = re.sub(r'\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))', '', input)

    return output
