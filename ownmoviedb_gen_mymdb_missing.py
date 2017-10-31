#!/usr/bin/env python
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
Writes a CSV file listing movies in the movie database that have no descriptive information.
Usage see below in Usage(), or invoke with '-h' or '--help'.

Supported platforms:
  Runs on any OS platform that has Python 2.7.
  Tested on Windows XP and Windows 7.

Prerequisites:
  1. Python 2.7, available from http://www.python.org
"""

import re, sys, glob, os, os.path, string, errno, locale, fnmatch, subprocess, xml.etree.ElementTree, datetime
from operator import itemgetter, attrgetter, methodcaller
import MySQLdb
from ownmoviedb import config, utils, version

my_name = os.path.basename(os.path.splitext(sys.argv[0])[0])

outfile_cp = "utf-8"            # code page used for output CSV file
out_file = "mymdb_missing.csv"

series_as_one_entry = False     # Boolean controlling that the report shortens series
                                # to one entry for the series (instead of reporting each episode).

filepath_begin_list = (         # file paths (or begins thereof) that will be listed
  "\\admauto",
  "\\Movies\\library\\Spielfilme\\",
  "\\Movies\\library\\Neu\\",
  "\\Movies\\library\\Kinderfilme\\",
  "\\Movies\\library\\Maerchen\\",
  "\\Movies\\library\\Krimiserien\\Wallander\\",
  "\\Movies\\library\\Krimiserien\\Barbarotti\\",
  "\\Movies\\library\\Krimiserien\\Brenner\\",
  "\\Movies\\library\\Krimiserien\\James Bond 007\\",
)

#------------------------------------------------------------------------------
def Usage ():
    """Print the command usage to stdout.
       Input:
         n/a
       Return:
         void.
    """

    print ""
    print "Writes a CSV file listing movies in the movie database that have no descriptive information."
    print "The CSV file can be used to add movies to MyMDb or directly into the movie database."
    print ""
    print "Usage:"
    print "  "+my_name+" [options]"
    print ""
    print "Options:"
    print "  -v          Verbose mode: Display additional messages."
    print "  -h, --help  Display this help text."
    print ""
    print "Movie database:"
    print "  MySQL host: "+config.MYSQL_HOST+" (default port 3306)"
    print "  MySQL user: "+config.MYSQL_USER+" (no password)"
    print "  MySQL database: "+config.MYSQL_DB
    print ""
    print "Filepaths on media server that are searched:"
    for filepath_begin in filepath_begin_list:
        print "  "+filepath_begin

    return


#------------------------------------------------------------------------------
# main routine
#

num_errors = 0                  # global number of errors
verbose_mode = False            # verbose mode, controlled by -v option
test_mode = False               # test mode, controlled by -t option


#
# command line parsing
#
pos_argv = []                   # positional command line parameters
_i = 1
while _i < len(sys.argv):
    arg = sys.argv[_i]
    if arg[0] == "-":
        if arg == "-h" or arg == "--help":
            Usage()
            exit(100)
        elif arg == "-a":
            update_all = True
        elif arg == "-v":
            verbose_mode = True
        elif arg == "-t":
            test_mode = True
        else:
            utils.ErrorMsg("Invalid command line option: "+arg)
            exit(100)
    else:
        pos_argv.append(arg)
    _i += 1
# drop _i

#
# more validiy checking on command line parameters
#
if len(pos_argv) > 0:
    utils.ErrorMsg("Too many command line arguments, invoke with '--help' for help.")
    exit(100)

if len(pos_argv) < 0:
    utils.ErrorMsg("Too few command line arguments, invoke with '--help' for help.")
    exit(100)

utils.Msg( my_name+" Version "+version.__version__)

# Connection to movie database
movies_conn = MySQLdb.connect( host=config.MYSQL_HOST, user=config.MYSQL_USER,
                               db=config.MYSQL_DB, use_unicode=True, charset='utf8')

_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute("SELECT * FROM Medium WHERE idMovie IS NULL AND idStatus IN ('WORK','SHARED','DISABLED')")
medium_rowlist = _cursor.fetchall()
_cursor.close()

medium_out_dict = dict()    # dictionary of titles of movie files without link to movie description, with access by pure normalized title + year
                            # key: pure normalized title '#' release year
                            # value: tuple: title_pure, title, year, filepath

for medium_row in medium_rowlist:

    medium_filepath = medium_row["FilePath"]

    for filepath_begin in filepath_begin_list:

        if medium_filepath.startswith(filepath_begin):

            series_title = medium_row["SeriesTitle"]
            title = medium_row["Title"]

            if series_as_one_entry and series_title != None:
                title_pure = utils.StripSquareBrackets(series_title)
            else:
                title_pure = utils.StripSquareBrackets(title)

            title_pure_normalized = utils.NormalizeTitle(title_pure)

            if title_pure_normalized not in medium_out_dict:

                year = medium_row["ReleaseYear"]
                filepath = medium_row["FilePath"]

                out_entry = title_pure, year, title, filepath

                medium_out_dict[title_pure_normalized] = out_entry

utils.Msg("Found "+str(len(medium_out_dict))+" movie files without movie information")


utils.Msg("Writing report file: "+out_file+" ...")

try:
    out_fp = open(out_file,"w")
except IOError as (errno, strerror):
    utils.ErrorMsg("Cannot open report file for writing: "+out_file+", "+strerror, num_errors)

else:

    out_key_list = sorted(list(medium_out_dict)) # list with keys of the dictionary

    for title_pure_normalized in out_key_list:

        out_entry = medium_out_dict[title_pure_normalized]

        title_pure, year, title, filepath = out_entry

        if title_pure == None:
            title_pure_u = ""
        elif type(title_pure) == unicode:
            title_pure_u = title_pure
        else:
            title_pure_u = title_pure.decode("ascii")
        title_pure_f = title_pure_u.encode(outfile_cp,'backslashreplace')

        if title == None:
            title_u = ""
        elif type(title) == unicode:
            title_u = title
        else:
            title_u = title.decode("ascii")
        title_f = title_u.encode(outfile_cp,'backslashreplace')

        if year == None:
            year_f = ""
        else:
            year_f = str(year)

        if filepath == None:
            filepath_f = ""
        else:
            filepath_f = filepath.encode(outfile_cp,'backslashreplace')

        out_fp.write('"'+title_pure_f+'","'+year_f+'","'+title_f+'","'+filepath_f+'"\n')

    out_fp.close()


if num_errors > 0:
    utils.ErrorMsg("Finished with "+str(num_errors)+" errors.")
    exit(12)
else:
    utils.Msg("Success.")
    exit(0)
