#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE

from setuptools import setup

setup(
    name='hsadownload',
    version='1.0.0dev',
    description='Herschel Archive Download Utilities',
    author='David Shupe',
    author_email='shupe@ipac.caltech.edu',
    license='BSD',
    py_modules = [
        'access',
        'getpacs'
    ]
)

