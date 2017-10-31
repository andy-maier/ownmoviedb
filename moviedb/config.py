# -*- coding: utf-8 -*-
"""Configuration parameters"""

__updated__ = "2016-10-18"


# OUTPUT_CP  = "cp850"                        # code page used for output messages
CMDLINE_CP = "cp1252"                       # code page used for parsing command line parameters
FILENAME_CP = "cp1252"                      # code page used for file names in Windows

# Information about the movie database on the MySQL server
MYSQL_HOST = "192.168.0.12"                 # IP addess or hostname of the MySQL server
MYSQL_PORT = None                           # port of the MySQL sever, None for default port (3306)
MYSQL_DB = "movies"                         # name of movies database in the MySQL sever
MYSQL_USER = "pyuser"                       # userid for logon to the MySQL sever
MYSQL_PASS = None                           # password for logon to the MySQL sever, None for no password

# Information about the movie files to scan, on the file server
_STD_SHARE = "\\\\"+MYSQL_HOST+"\\share"    # Standard UNC resource on file server (Using Windows path separators)
_STD_PATTERNS = [                           # Standard file patterns to scan
    "*.mp4",
    "*.avi",
    "*.mkv",
    "*.flv",
]
FILE_SOURCES = [                            # Movie files to scan, as a list of dictionaries
    {
        "res":          _STD_SHARE,         # UNC name of resource on file server
        "dir":          "\\admauto",        # subtree to scan, on that resource (using Windows path separators)
        "folder_root":  "\\Special\\AdmAuto",  # root of display folder path for the files in this subtree.
                                            #   The display folder path of a file is this root, plus the
                                            #   directory path relative to "dir".
        "patterns":     _STD_PATTERNS,      # file patterns to scan, in that subtree
        "status":       "WORK",             # status of movie files found in this subtree,
                                            #   using values of idStatus column in movies.FixedStatus table
    },
    {
        "res":          _STD_SHARE,
        "dir":          "\\Movies\\MissingParts",
        "folder_root":  "\\Special\\MissingParts",
        "patterns":     _STD_PATTERNS,
        "status":       "MISSINGPARTS",
    },
    {
        "res":          _STD_SHARE,
        "dir":          "\\Movies\\LowResolution+Duplicates",
        "folder_root":  "\\Special\\LowResolution+Duplicates",
        "patterns":     _STD_PATTERNS,
        "status":       "DUPLICATE",
    },
    {
        "res":          _STD_SHARE,
        "dir":          "\\Movies\\library",
        "folder_root":  "\\",
        "patterns":     _STD_PATTERNS,
        "status":       "SHARED",
    },
    {
        "res":          _STD_SHARE,
        "dir":          "\\Movies\\library.disabled",
        "folder_root":  "\\",
        "patterns":     _STD_PATTERNS,
        "status":       "DISABLED",
    },
]
