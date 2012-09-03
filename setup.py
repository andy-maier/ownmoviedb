#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# To make this package, run from within this directory (in Windows):
#   if exist MANIFEST del MANIFEST
#   python setup.py build sdist -d ../dist

'''Utilities for movies database'''

from distutils.core import setup
import os.path, sys

# Execute moviedb/version.py using its absolute path, so that setup.py can be run with
# any current working directory.
version_py = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]),'moviedb/version.py'))
execfile(version_py) # defines __version__

setup(
    name             = 'moviedb',
    version          = __version__,
    description      = __doc__,
    long_description = __doc__,
    author           = 'Andreas Maier',
    author_email     = 'andreas.r.maier@gmx.de',
    url              = None,
    platforms        = ['any'],
    packages         = ['moviedb'],
    scripts          = ['moviedb_scan_files.bat','moviedb_scan_files.py',
                        'moviedb_import_movies.bat','moviedb_import_movies.py',
                        'moviedb_link_movies.bat','moviedb_link_movies.py',
                        'moviedb_gen_mymdb_missing.bat','moviedb_gen_mymdb_missing.py',
                        'moviedb_gen_movielist.bat','moviedb_gen_movielist.py',
                        'moviedb_check.bat','moviedb_check.py',
                        'moviedb_dailyrun.bat'],
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
