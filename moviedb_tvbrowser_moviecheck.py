#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
# coding: utf-8
#
# This script is a device for TV-Browser Recording Control.
# It checks whether a given movie is present in the movie database and displays the result.
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
# Change log:
#   V1.2.2 2012-09-15 AM
#       Integrated into moviedb project.


import sys, os.path
import MySQLdb
from moviedb import config, utils


my_name = os.path.basename(os.path.splitext(sys.argv[0])[0])

#------------------------------------------------------------------------------
def Usage ():
    """Print the command usage to stdout.
       Input:
         n/a
       Return:
         void.
    """

    print ""
    print "TV-Browser Recording Control script that checks for presence of movie in movie database."
    print ""
    print "Usage:"
    print "  "+my_name+" [options]"
    print ""
    print "Options for specifying the movie:"
    print "  -title \"{title}\""
    print "  -originaltitle \"{originaltitle}\""
    print "  -episodetitle \"{episodetitle}\""
    print "  -originalepisodetitle \"{originalepisodetitle}\""
    print "  -episodenumber \"{episodenumber}\""
    print ""
    print "Other options:"
    print "  -v                         Verbose mode: Display additional messages."
    print ""

    return


#------------------------------------------------------------------------------
def DisplayMedium(medium_row):

    utils.Msg("Movie file found:")

    utils.Msg("  File Path: "+medium_row["FilePath"])

    if medium_row["VideoBitrate"] != None:
        video_bitrate = str(medium_row["VideoBitrate"])+" kbit/s"
    else:
        video_bitrate = "unknown"
    utils.Msg("  Video Bitrate: "+video_bitrate)

    if medium_row["DisplayAspectRatio"] != None:
        dar = str(medium_row["DisplayAspectRatio"])
        utils.Msg("  Display Aspect Ratio: "+dar)

    if medium_row["OriginalDisplayAspectRatio"] != None:
        odar = str(medium_row["OriginalDisplayAspectRatio"])
        utils.Msg("  Original Display Aspect Ratio: "+odar)


#------------------------------------------------------------------------------
# main routine
#


num_errors = 0

#
# command line parsing
#

search_title = None                     # title
search_original_title = None            # original title
search_episode_title = None             # episode title
search_original_episode_title = None    # original episode title
search_episode_number = None            # episode number

pos_argv = []                           # positional command line parameters

_i = 1
while _i < len(sys.argv):
    arg = sys.argv[_i]
    if arg[0] == "-":
        if arg == "-h" or arg == "--help":
            Usage()
            exit(100)
        elif arg == "-title":
            _i += 1
            if _i == len(sys.argv):
                utils.ErrorMsg("Missing parameter for -title option, invoke with -h or --help for help.")
                num_errors += 1
                break
            if sys.argv[_i] != "":
                search_title = sys.argv[_i].strip('"').decode(config.cmdline_cp)
        elif arg == "-originaltitle":
            _i += 1
            if _i == len(sys.argv):
                utils.ErrorMsg("Missing parameter for -originaltitle option, invoke with -h or --help for help.")
                num_errors += 1
                break
            if sys.argv[_i] != "":
                search_original_title = sys.argv[_i].strip('"').decode(config.cmdline_cp)
        elif arg == "-episodetitle":
            _i += 1
            if _i == len(sys.argv):
                utils.ErrorMsg("Missing parameter for -episodetitle option, invoke with -h or --help for help.")
                num_errors += 1
                break
            if sys.argv[_i] != "":
                search_episode_title = sys.argv[_i].strip('"').decode(config.cmdline_cp)
        elif arg == "-originalepisodetitle":
            _i += 1
            if _i == len(sys.argv):
                utils.ErrorMsg("Missing parameter for -originalepisodetitle option, invoke with -h or --help for help.")
                num_errors += 1
                break
            if sys.argv[_i] != "":
                search_original_episode_title = sys.argv[_i].strip('"').decode(config.cmdline_cp)
        elif arg == "-episodenumber":
            _i += 1
            if _i == len(sys.argv):
                utils.ErrorMsg("Missing parameter for -episodenumber option, invoke with -h or --help for help.")
                num_errors += 1
                break
            if sys.argv[_i] != "":
                search_episode_number = sys.argv[_i].strip('"').decode(config.cmdline_cp)

        else:
            utils.ErrorMsg("Invalid command line option: "+arg+", invoke with -h or --help for help.")
            num_errors += 1
    else:
        pos_argv.append(arg)
    _i += 1


#
# more validiy checking on command line parameters
#
if num_errors > 0:
    exit(100)

if len(pos_argv) > 0:
    utils.ErrorMsg("Too many command line arguments: "+" ".join(pos_argv)+", invoke with -h or --help for help.")
    exit(100)

if search_title == None and search_original_title == None and search_episode_title == None\
and search_original_episode_title == None and search_episode_number == None:
    utils.ErrorMsg("No movie search options specified, invoke with -h or --help for help.")
    exit(100)


search_title_normalized = utils.NormalizeTitle(search_title)
search_original_title_normalized = utils.NormalizeTitle(search_original_title)


# Connection to movie database
movies_conn = MySQLdb.connect(host=config.mysql_host,user=config.mysql_user,db=config.mysql_db,use_unicode=True)

_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute(u"SELECT * FROM Medium")
medium_rowlist = _cursor.fetchall()
_cursor.close()

movies_conn.commit()


medium_tn_dict = dict()         # dictionary of movie files
                                # key: normalized title
                                # value: tuple with indexes into medium_rowlist array (0-based)

medium_stn_dict = dict()        # dictionary of movie files
                                # key: normalized series title
                                # value: tuple with indexes into medium_rowlist array (0-based)

medium_etn_dict = dict()        # dictionary of movie files
                                # key: normalized episode title
                                # value: tuple with indexes into medium_rowlist array (0-based)

i = 0
for medium_row in medium_rowlist:

    title_normalized = utils.NormalizeTitle(medium_row["Title"])
    series_title_normalized = utils.NormalizeTitle(medium_row["SeriesTitle"])
    episode_title_normalized = utils.NormalizeTitle(medium_row["EpisodeTitle"])

    tn_key = title_normalized
    if tn_key not in medium_tn_dict:
        medium_tn_dict[tn_key] = []
    medium_tn_dict[tn_key].append(i)

    if series_title_normalized != None:
        stn_key = series_title_normalized
        if stn_key not in medium_stn_dict:
            medium_stn_dict[stn_key] = []
        medium_stn_dict[stn_key].append(i)

    if episode_title_normalized != None:
        etn_key = episode_title_normalized
        if etn_key not in medium_etn_dict:
            medium_etn_dict[etn_key] = []
        medium_etn_dict[etn_key].append(i)

    i += 1

tn_key = search_title_normalized
otn_key = search_original_title_normalized

num_found = 0
if tn_key in medium_tn_dict:
    # Title of movie to be checked matches title of movie file
    for i in medium_tn_dict[tn_key]:
        num_found += 1
        DisplayMedium(medium_rowlist[i])

if otn_key in medium_tn_dict:
    # Original title of movie to be checked matches title of movie file
    for i in medium_tn_dict[otn_key]:
        num_found += 1
        DisplayMedium(medium_rowlist[i])

if num_found == 0:
    utils.Msg("Movie file not found in movies database.")


if num_errors > 0:
    utils.ErrorMsg("Finished with "+str(num_errors)+" errors.")
    exit(12)
else:
    # Success
    exit(1)
