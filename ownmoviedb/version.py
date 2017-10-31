# -*- coding: utf-8 -*-
# coding: utf-8
# -----------------------------------------------------------------------------
# Copyright 2012-2017 Andreas Maier. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

"""
Module defining package version for ownmoviedb project.
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
__version__ = pbr.version.VersionInfo('ownmoviedb').release_string()
