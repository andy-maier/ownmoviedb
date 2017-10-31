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
Configuration parameters for ownmoviedb project.
"""

# Code page used for output messages
# OUTPUT_CP  = "cp850"

# Code page used for parsing command line parameters
CMDLINE_CP = "cp1252"

# Code page used for file names in Windows
FILENAME_CP = "cp1252"
#
# Information about the movie database on the MySQL server
#

# IP addess or hostname of the MySQL server
MYSQL_HOST = "192.168.0.12"

# Port of the MySQL sever, None for default port (3306)
MYSQL_PORT = None

# Name of database in the MySQL sever
MYSQL_DB = "ownmoviedb"

# Userid for logon to the MySQL sever
MYSQL_USER = "pyuser"

# Password for logon to the MySQL sever, None for no password
MYSQL_PASS = None

#
# Information about the movie files to scan, on the file server
#

# Standard UNC resource on file server (Using Windows path separators)
_STD_SHARE = "\\\\" + MYSQL_HOST + "\\share"

# Standard file patterns to scan
_STD_PATTERNS = [
    "*.mp4",
    "*.avi",
    "*.mkv",
    "*.flv",
]

# Movie files to scan, as a list of dictionaries, with the following keys:
# * 'res': UNC name of resource on file server
# * 'dir': Subtree to scan, on that resource (using Windows path separators)
# * 'folder_root': Root of display folder path for the files in this subtree.
#   The display folder path of a file is this root, plus the directory path
#   relative to "dir".
# * 'patterns': File patterns to scan, in that subtree.
# * 'status': Status of movie files found in this subtree, using values of
#   idStatus column in movies.FixedStatus table.
FILE_SOURCES = [
    {
        "res": _STD_SHARE,
        "dir": "\\admauto",
        "folder_root": "\\Special\\AdmAuto",
        "patterns": _STD_PATTERNS,
        "status": "WORK",
    },
    {
        "res": _STD_SHARE,
        "dir": "\\Movies\\MissingParts",
        "folder_root": "\\Special\\MissingParts",
        "patterns": _STD_PATTERNS,
        "status": "MISSINGPARTS",
    },
    {
        "res": _STD_SHARE,
        "dir": "\\Movies\\LowResolution+Duplicates",
        "folder_root": "\\Special\\LowResolution+Duplicates",
        "patterns": _STD_PATTERNS,
        "status": "DUPLICATE",
    },
    {
        "res": _STD_SHARE,
        "dir": "\\Movies\\library",
        "folder_root": "\\",
        "patterns": _STD_PATTERNS,
        "status": "SHARED",
    },
    {
        "res": _STD_SHARE,
        "dir": "\\Movies\\library.disabled",
        "folder_root": "\\",
        "patterns": _STD_PATTERNS,
        "status": "DISABLED",
    },
]
