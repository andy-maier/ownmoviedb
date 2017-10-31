#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
# Configuration parameters for movies_* scripts
#

# output_cp  = "cp850"                        # code page used for output messages
cmdline_cp = "cp1252"                       # code page used for parsing command line parameters
filename_cp = "cp1252"                      # code page used for file names in Windows

# Information about the movie database on the MySQL server
mysql_host = "192.168.0.12"                 # IP addess or hostname of the MySQL server
mysql_port = None                           # port of the MySQL sever, None for default port (3306)
mysql_db   = "movies"                       # name of movies database in the MySQL sever
mysql_user = "pyuser"                       # userid for logon to the MySQL sever
mysql_pass = None                           # password for logon to the MySQL sever, None for no password

# Information about the movie files to scan, on the file server
_std_share = "\\\\"+mysql_host+"\\share"    # Standard UNC resource on file server (Using Windows path separators)
_std_patterns = [                           # Standard file patterns to scan
    "*.mp4",
    "*.avi",
    "*.mkv",
    "*.flv",
]
file_sources = [                            # Movie files to scan, as a list of dictionaries
    {
        "res":          _std_share,         # UNC name of resource on file server
        "dir":          "\\admauto",        # subtree to scan, on that resource (using Windows path separators)
        "folder_root":  "\\Special\\AdmAuto",  # root of display folder path for the files in this subtree.
                                            #   The display folder path of a file is this root, plus the
                                            #   directory path relative to "dir".
        "patterns":     _std_patterns,      # file patterns to scan, in that subtree
        "status":       "WORK",             # status of movie files found in this subtree,
                                            #   using values of idStatus column in movies.FixedStatus table
    },
    {
        "res":          _std_share,
        "dir":          "\\Movies\\MissingParts",
        "folder_root":  "\\Special\\MissingParts",
        "patterns":     _std_patterns,
        "status":       "MISSINGPARTS",
    },
    {
        "res":          _std_share,
        "dir":          "\\Movies\\LowResolution+Duplicates",
        "folder_root":  "\\Special\\LowResolution+Duplicates",
        "patterns":     _std_patterns,
        "status":       "DUPLICATE",
    },
    {
        "res":          _std_share,
        "dir":          "\\Movies\\share",
        "folder_root":  "\\",
        "patterns":     _std_patterns,
        "status":       "SHARED",
    },
    {
        "res":          _std_share,
        "dir":          "\\Movies\\share.disabled",
        "folder_root":  "\\",
        "patterns":     _std_patterns,
        "status":       "DISABLED",
    },
]
