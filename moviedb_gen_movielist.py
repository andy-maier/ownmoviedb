#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf-8
#
# Generates a CSV file containing the list of movie files in the movies database
# Usage see below in Usage(), or invoke with '-h' or '--help'.
#
# Supported platforms:
#   Runs on any OS platform that has Python 2.7.
#   Tested on Windows XP and Windows 7.
#
# Prerequisites:
#   1. Python 2.7, available from http://www.python.org
#
# Change log:
#   V1.1.0 2012-06-24
#     Added Homenet rating columns based on UserMovieOpinion table.
#     Fixed Excel CSV issue by replacing \r with \n in content of string cells, because \r triggers new row in Excel.
#   V1.1.1 2012-08-13
#   V1.3.1 2013-05-19
#     Renamed output CSV file to AM_MovieList.csv.
#     Added DAR and ODAR columns to CSV file.

import re, sys, glob, os, os.path, string, errno, locale, fnmatch, subprocess, xml.etree.ElementTree, datetime
from operator import itemgetter, attrgetter, methodcaller
import MySQLdb
from moviedb import config, utils, version

my_name = os.path.basename(os.path.splitext(sys.argv[0])[0])

outcsv_file = "AM_MovieList.csv"  # file name of output CSV file
outcsv_cp = "utf-8"               # code page used for output CSV file

filepath_begin_list = (         # file paths (or begins thereof) with movie files that will be listed
  "\\admauto",
  "\\Movies\\library",
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
    print "Generates a CSV file containing the list of movie files in the movies database."
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
    print "Generated CSV file: "+outcsv_file
    print ""
    print "Movie files that begin with the following path are included in the list:"
    for filepath_begin in filepath_begin_list:
        print "  "+filepath_begin

    return


#------------------------------------------------------------------------------
def OutStr(db_value, disp_type=None):

    if disp_type == None: # as string
        if db_value == None:
            out_str_u = u''
        elif type(db_value) == unicode:
            out_str_u = db_value
        elif type(db_value) == str:
            out_str_u = db_value.decode("ascii")
        elif type(db_value) in (int,long,float):
            out_str_u = str(db_value).decode("ascii")
        else:
            raise TypeError("Invalid type of db_value: "+str(type(db_value)))
        # \n needed in Excel CSV for multi-line strings because \r triggers new row on import.
        newline_char = "\n"
        out_str_u = out_str_u.replace("\r\n",newline_char).replace("\n",newline_char).replace("\r",newline_char)
        # Replace double quotes with single quotes. That seems safer than escaping or doubling them.
        out_str_u = out_str_u.replace('"',"'")
    else:
        if disp_type == 'boolean':
            if db_value == None:
                out_str_u = u''
            elif int(db_value) > 0:
                out_str_u = "ja"
            else:
                out_str_u = "nein"
        elif disp_type == 'int':
            if db_value == None:
                out_str_u = u''
            else:
                out_str_u = str(int(db_value)).decode("ascii")
        elif disp_type == 'float':
            if db_value == None:
                out_str_u = u''
            else:
                out_str_u = str(float(db_value)).decode("ascii")
        else:
            raise TypeError("Invalid disp_type: "+str(disp_type))

    out_str = out_str_u.encode(outcsv_cp,'backslashreplace')

    return out_str


#------------------------------------------------------------------------------
# main routine
#

num_errors = 0                  # global number of errors
verbose_mode = False            # verbose mode, controlled by -v option


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
        elif arg == "-v":
            verbose_mode = True
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

utils.Msg("Reading movie files from movies database ...")

movies_conn = MySQLdb.connect( host=config.MYSQL_HOST, user=config.MYSQL_USER,
                               db=config.MYSQL_DB, use_unicode=True, charset='utf8')

_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)

_cursor.execute("SELECT\
  Medium.Title AS Title,\
  Movie.OriginalTitle AS OriginalTitle,\
  Medium.SeriesTitle AS SeriesTitle,\
  Medium.EpisodeTitle AS EpisodeTitle,\
  Medium.EpisodeId AS EpisodeId,\
  IFNULL(Medium.ReleaseYear,Movie.ReleaseYear) AS ReleaseYear,\
  Medium.Duration AS Duration,\
  Medium.Language AS Language,\
  FixedQuality.Name AS Quality,\
  Medium.DesiredDisplayAspectRatioWidth AS DesiredDisplayAspectRatioWidth,\
  Medium.DesiredDisplayAspectRatioHeight AS DesiredDisplayAspectRatioHeight,\
  Medium.DisplayAspectRatio AS DisplayAspectRatio,\
  Medium.OriginalDisplayAspectRatio AS OriginalDisplayAspectRatio,\
  FixedStatus.Name AS Status,\
  Medium.Uncut AS Uncut,\
  Medium.TechnicalFlaws AS TechnicalFlaws,\
  FixedContainerFormat.Name AS ContainerFormat,\
  FixedVideoFormat.Name AS VideoFormat,\
  Medium.VideoFormatProfile AS VideoFormatProfile,\
  Medium.VideoSamplingWidth AS VideoSamplingWidth,\
  Medium.VideoSamplingHeight AS VideoSamplingHeight,\
  Medium.VideoBitrate AS VideoBitrate,\
  Medium.VideoFramerate AS VideoFramerate,\
  FixedVideoFramerateMode.Name AS VideoFramerateMode,\
  FixedAudioFormat.Name AS AudioFormat,\
  Medium.AudioFormatProfile AS AudioFormatProfile,\
  Medium.AudioBitrate AS AudioBitrate,\
  FixedAudioBitrateMode.Name AS AudioBitrateMode,\
  Medium.AudioSamplingRate AS AudioSamplingRate,\
  Cabinet.SMBServerHost AS ServerHost,\
  Cabinet.SMBServerShare AS ServerShare,\
  Medium.FilePath AS FilePath, \
  Movie.Genres AS Genres,\
  Movie.Directors AS Directors,\
  Movie.Actors AS Actors,\
  Movie.Description AS Description,\
  Movie.FSK AS FSK,\
  Movie.IMDbLink AS IMDbLink,\
  Movie.IMDbRating AS IMDbRating,\
  Movie.IMDbRaters AS IMDbRaters,\
  Movie.OFDbLink AS OFDbLink,\
  Movie.OFDbRating AS OFDbRating,\
  Movie.OFDbRaters AS OFDbRaters, \
  (SELECT AVG(Rating) FROM UserMovieOpinion WHERE idMovie = Medium.idMovie) AS HomenetRating,\
  (SELECT COUNT(Rating) FROM UserMovieOpinion WHERE idMovie = Medium.idMovie) AS HomenetRaters, \
  (SELECT COUNT(IsRecommended) FROM UserMovieOpinion WHERE idMovie = Medium.idMovie AND IsRecommended = True) AS HomenetRecommenders \
FROM Medium\
  LEFT JOIN FixedStatus ON FixedStatus.idStatus = Medium.idStatus\
  LEFT JOIN FixedQuality ON FixedQuality.idVideoQuality = Medium.idQuality\
  LEFT JOIN FixedContainerFormat ON FixedContainerFormat.idContainerFormat = Medium.idContainerFormat\
  LEFT JOIN FixedVideoFormat ON FixedVideoFormat.idVideoFormat = Medium.idVideoFormat\
  LEFT JOIN FixedVideoFramerateMode ON FixedVideoFramerateMode.idVideoFramerateMode = Medium.idVideoFramerateMode\
  LEFT JOIN FixedAudioFormat ON FixedAudioFormat.idAudioFormat = Medium.idAudioFormat\
  LEFT JOIN FixedAudioBitrateMode ON FixedAudioBitrateMode.idAudioBitrateMode = Medium.idAudioBitrateMode\
  LEFT JOIN Movie ON Movie.idMovie = Medium.idMovie\
  LEFT JOIN Cabinet ON Cabinet.idCabinet = Medium.idCabinet \
WHERE Medium.idStatus IN ('SHARED','WORK','DISABLED')\
  AND Medium.idMediumType IN ('FILE') \
ORDER BY Title, ReleaseYear")

medium_rowlist = _cursor.fetchall()
_cursor.close()

medium_out_list = list()    # list of movie files to be generated
                            # value of each list entry: dictionary with select result columns as keys

for medium_row in medium_rowlist:
    medium_filepath = medium_row["FilePath"]
    for filepath_begin in filepath_begin_list:
        if medium_filepath.startswith(filepath_begin):
            medium_out_list.append(medium_row)


utils.Msg("Writing CSV output file: "+outcsv_file+" ...")

try:
    outcsv_fp = open(outcsv_file,"wb")
except IOError as (errno, strerror):
    utils.ErrorMsg("Cannot open output file for writing: "+outcsv_file+", "+strerror, num_errors)

else:
    bom = "\xef\xbb\xbf"

    hdr = \
        '"Titel",' +\
        '"Originaltitel",' +\
        '"Serientitel",' +\
        '"Episodentitel",' +\
        '"EpisodenId",' +\
        '"Jahr",' +\
        '"Laenge [min]",' +\
        '"Sprache",' +\
        '"Qualitaet",' +\
        '"Aspect Ratio",' +\
        '"DAR Feld",' +\
        '"ODAR Feld",' +\
        '"Schnitt Status",' +\
        '"Technische Maengel",' +\
        '"Container Format",' +\
        '"Video Format",' +\
        '"Video Profil",' +\
        '"Video Sampling [px]",' +\
        '"Video Bit Rate [kbit/s]",' +\
        '"Video Frame Rate [f/s]",' +\
        '"Video Frame Rate Mode",' +\
        '"Audio Format",' +\
        '"Audio Profil",' +\
        '"Audio Bit Rate [kbit/s]",' +\
        '"Audio Bit Rate Mode",' +\
        '"Audio Sampling Rate [Hz]",' +\
        '"File Path",' +\
        '"Genres",' +\
        '"Regisseure",' +\
        '"Schauspieler",' +\
        '"Beschreibung",' +\
        '"FSK",' +\
        '"IMDb Link",' +\
        '"IMDb Rating",' +\
        '"IMDb Raters",' +\
        '"OFDb Link",' +\
        '"OFDb Rating",' +\
        '"OFDb Raters",' +\
        '"Homenet Rating",' +\
        '"Homenet Raters",' +\
        '"Homenet Recommenders"' +\
        '\r\n'

    outcsv_fp.write(bom)
    outcsv_fp.write(hdr)

    for out_entry in medium_out_list:

        row = \
            '"'+OutStr(out_entry["Title"])+'",'+\
            '"'+OutStr(out_entry["OriginalTitle"])+'",'+\
            '"'+OutStr(out_entry["SeriesTitle"])+'",'+\
            '"'+OutStr(out_entry["EpisodeTitle"])+'",'+\
            '"'+OutStr(out_entry["EpisodeId"])+'",'+\
            ''+OutStr(out_entry["ReleaseYear"],"int")+','+\
            ''+OutStr(out_entry["Duration"],"int")+','+\
            '"'+OutStr(out_entry["Language"])+'",'+\
            '"'+OutStr(out_entry["Quality"])+'",'+\
            '"'+("" if out_entry["DesiredDisplayAspectRatioWidth"] == None
                else OutStr(out_entry["DesiredDisplayAspectRatioWidth"])+'x'+OutStr(out_entry["DesiredDisplayAspectRatioHeight"]))+'",'+\
            ''+OutStr(out_entry["DisplayAspectRatio"],"float")+','+\
            ''+OutStr(out_entry["OriginalDisplayAspectRatio"],"float")+','+\
            '"'+("Ungeschnitten" if out_entry["Uncut"] > 0 else "Geschnitten")+'",'+\
            '"'+OutStr(out_entry["TechnicalFlaws"])+'",'+\
            '"'+OutStr(out_entry["ContainerFormat"])+'",'+\
            '"'+OutStr(out_entry["VideoFormat"])+'",'+\
            '"'+OutStr(out_entry["VideoFormatProfile"])+'",'+\
            '"'+("" if out_entry["VideoSamplingWidth"] == None
                else OutStr(out_entry["VideoSamplingWidth"])+'x'+OutStr(out_entry["VideoSamplingHeight"]))+'",'+\
            ''+OutStr(out_entry["VideoBitrate"],"int")+','+\
            ''+OutStr(out_entry["VideoFramerate"],"int")+','+\
            '"'+("" if out_entry["VideoFramerate"] == None
                else
                    ("C" if out_entry["VideoFramerateMode"] == "Constant"
                    else "V" if out_entry["VideoFramerateMode"] == "Variable"
                    else "?"))+'",'+\
            '"'+OutStr(out_entry["AudioFormat"])+'",'+\
            '"'+OutStr(out_entry["AudioFormatProfile"])+'",'+\
            ''+OutStr(out_entry["AudioBitrate"],"int")+','+\
            '"'+("" if out_entry["AudioBitrate"] == None
                else
                    ("C" if out_entry["AudioBitrateMode"] == "Constant"
                    else "V" if out_entry["AudioBitrateMode"] == "Variable"
                    else "?"))+'",'+\
            ''+OutStr(out_entry["AudioSamplingRate"],"int")+','+\
            '"'+OutStr(out_entry["FilePath"])+'",'+\
            '"'+OutStr(out_entry["Genres"])+'",'+\
            '"'+OutStr(out_entry["Directors"])+'",'+\
            '"'+OutStr(out_entry["Actors"])+'",'+\
            '"'+OutStr(out_entry["Description"])+'",'+\
            ''+OutStr(out_entry["FSK"],"int")+','+\
            '"'+OutStr(out_entry["IMDbLink"])+'",'+\
            ''+OutStr(out_entry["IMDbRating"],"float")+','+\
            ''+OutStr(out_entry["IMDbRaters"],"int")+','+\
            '"'+OutStr(out_entry["OFDbLink"])+'",'+\
            ''+OutStr(out_entry["OFDbRating"],"float")+','+\
            ''+OutStr(out_entry["OFDbRaters"],"int")+','+\
            ''+OutStr(out_entry["HomenetRating"],"float")+','+\
            ''+OutStr(out_entry["HomenetRaters"],"int")+','+\
            ''+OutStr(out_entry["HomenetRecommenders"],"int")+''+\
            '\r\n'

        outcsv_fp.write(row)

    outcsv_fp.close()


if num_errors > 0:
    utils.ErrorMsg("Finished with "+str(num_errors)+" errors.")
    exit(12)
else:
    utils.Msg("Success.")
    exit(0)
