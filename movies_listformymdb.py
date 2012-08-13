#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
# coding: utf-8
#
# This script lists movies that need MyMDb import data (i.e. that have no description etc)
#
# Invoke with '-?' or '--help' for help.
#
# Supported platforms:
#   Runs on any OS platform that has Python 2.7.
#   Tested on Windows XP.
#
# Prerequisites:
#   1. Python 2.7, available from http://www.python.org
#

my_name = "movies_listformymdb"
my_version = "1.0.1"

import re, sys, glob, os, os.path, string, errno, locale, fnmatch, subprocess, xml.etree.ElementTree, datetime
from operator import itemgetter, attrgetter, methodcaller
import MySQLdb
from movies_conf import *
from movies_utils import NormalizeTitle, StripSquareBrackets

outfile_cp = "utf-8"            # code page used for output CSV file
out_file = "mymdb_missing.csv"

filepath_begin_list = (         # file paths (or begins thereof) that will be listed
  "\\admauto",
  "\\Movies\\share\\Spielfilme",
  "\\Movies\\share\\Kinderfilme",
)

num_errors = 0                  # global number of errors
quiet_mode = True               # quiet mode, controlled by -v option
test_mode = False               # test mode, controlled by -t option
update_all = False              # Update all movies, instead of just those whose records are outdated, controlled by -a option

#------------------------------------------------------------------------------
def Usage ():
    """Print the command usage to stdout.
       Input:
         n/a
       Return:
         void.
    """

    print ""
    print "Lists movies in the movies database on a MySQL server that have no description etc. and"
    print "writes a CSV output file with their movie titles and file path."
    print ""
    print "Usage:"
    print "  "+my_name+" [options]"
    print ""
    print "Options:"
    print "  -v          Verbose mode: Display additional messages."
    print ""
    print "MySQL server:"
    print "  host: "+mysql_host+" (default port 3306)"
    print "  user: "+mysql_user+" (no password)"
    print ""
    print "Filepaths on media server that are searched:"
    for filepath_begin in filepath_begin_list:
        print "  "+filepath_begin

    return


#------------------------------------------------------------------------------
def ErrorMsg (msg):
    """Print an error message to stderr.
       Input:
         msg: Error message string.
       Return:
         void.
    """

    global num_errors, output_cp

    msg = "Error: "+msg

    if type(msg) == unicode:
        msgu = msg
    else:
        msgu = msg.decode("ascii")

    text = msgu.encode(output_cp,'backslashreplace')

    print >>sys.stderr, text
    sys.stderr.flush()

    num_errors += 1

    return


#------------------------------------------------------------------------------
def Msg (msg):
    """Print a message to stdout, unless quiet mode is active.
       Input:
         msg: Message string.
       Return:
         void.
    """

    global quiet_mode, output_cp

    if quiet_mode == False:

        if type(msg) == unicode:
            msgu = msg
        else:
            msgu = msg.decode("ascii")

        # print "Debug: msgu: type = "+str(type(msgu))+", repr = "+repr(msgu)

        text = msgu.encode(output_cp,'backslashreplace')

        # print "Debug: text: type = "+str(type(text))+", repr = "+repr(text)

        print >>sys.stdout, text
        sys.stdout.flush()

    return


#------------------------------------------------------------------------------
# main routine
#


#
# command line parsing
#
pos_argv = []                   # positional command line parameters
_i = 1
while _i < len(sys.argv):
    arg = sys.argv[_i]
    if arg[0] == "-":
        if arg == "-?" or arg == "--help":
            Usage()
            exit(100)
        elif arg == "-a":
            update_all = True
        elif arg == "-v":
            quiet_mode = False
        elif arg == "-t":
            test_mode = True
        else:
            ErrorMsg("Invalid command line option: "+arg)
    else:
        pos_argv.append(arg)
    _i += 1
# drop _i

#
# more validiy checking on command line parameters
#
if len(pos_argv) > 0:
    ErrorMsg("Too many command line arguments, invoke with '--help' for help.")
    exit(100)

if len(pos_argv) < 0:
    ErrorMsg("Too few command line arguments, invoke with '--help' for help.")
    exit(100)

Msg( my_name+" Version "+my_version)

# Connection to movie database
movies_conn = MySQLdb.connect(host=mysql_host,user=mysql_user,db=mysql_db,use_unicode=True)

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

            if series_title != None:
                title_pure = StripSquareBrackets(series_title)
            else:
                title_pure = StripSquareBrackets(title)

            title_pure_normalized = NormalizeTitle(title_pure)

            if title_pure_normalized not in medium_out_dict:

                year = medium_row["ReleaseYear"]
                filepath = medium_row["FilePath"]

                out_entry = title_pure, year, title, filepath

                medium_out_dict[title_pure_normalized] = out_entry

Msg("Found "+str(len(medium_out_dict))+" movie files without movie information")

# Msg("Debug: medium_out_dict: "+repr(medium_out_dict))


Msg("Writing MyMDb import file: "+out_file+" ...")

try:
    out_fp = open(out_file,"w")
except IOError as (errno, strerror):
    ErrorMsg("Cannot open output file for writing: "+out_file+", "+strerror)

else:

    out_key_list = sorted(list(medium_out_dict)) # list with keys of the dictionary

    # Msg("Debug: out_key_list: "+repr(out_key_list))

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
    ErrorMsg("Finished with "+str(num_errors)+" errors.")
    exit(12)
else:
    exit(0)

