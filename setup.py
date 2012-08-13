#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# To make this package, run from within this directory (in Windows):
#   if exist MANIFEST del MANIFEST
#   python setup.py build sdist -d ../dist

'''Utilities for movies database'''

from distutils.core import setup

setup(
    name             = 'movies',
    version          = '1.1.1',
    description      = __doc__,
    long_description = __doc__,
    author           = 'Andreas Maier',
    author_email     = 'andreas.r.maier@gmx.de',
    url              = None,
    platforms        = ['any'],
    py_modules       = ['movies_utils','movies_conf'],
    scripts          = ['movies_check.bat','movies_check.py',
                        'movies_genlist.bat','movies_genlist.py',
                        'movies_linkmovies.bat','movies_linkmovies.py',
                        'movies_listformymdb.bat','movies_listformymdb.py',
                        'movies_updatemedia.bat','movies_updatemedia.py',
                        'movies_updatemovies.bat','movies_updatemovies.py',
                        'movies_dailyrun.bat'],
    classifiers      = [
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users",
        "Environment :: Console",
        "Topic :: Video",
    ],
    license          = None,
    # options supported only if we used setuptools:
    #keywords         = "Movies Video",
    #install_requires = [
    #],
)
