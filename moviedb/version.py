# -*- coding: utf-8 -*-
# coding: utf-8
"""
Module defining package version for moviedb project.
"""

import sys
import pbr.version

__all__ = ['__version__']

#: The full version of this package including any development levels, as a
#: string.
#:
#: Possible formats for this version string are:
#:
#: * "M.N.P.devD": Development level D of a not yet released assumed M.N.P
#:   version
#: * "M.N.P": A released M.N.P version
__version__ = pbr.version.VersionInfo('moviedb').release_string()
