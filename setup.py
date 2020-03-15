#!/usr/bin/env python3

# TODO:
# need to set up the datadir for the config and shiz

# import setuptools

# from distutils.core import setup
from setuptools import find_packages, setup

setup(
    name='faze',
    version='0.5',
    description='Modular pentesting tool.',
    url='https://github.com/KhasMek/faze',
    author='Khas Mek',
    include_package_data=True,
    dependency_links=[
        'git+https://github.com/aboul3la/Sublist3r.git@master#egg=Sublist3r-1.0'
    ],
    install_requires=[
        'colorama',
        'elasticsearch',
        'nessrest',
        'pygeoip',
        'python-nmap',
        'python-libnmap',
        'requests',
        'Sublist3r',
        'tldextract'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
        'faze = faze.faze:main'
        ]
    },
)
