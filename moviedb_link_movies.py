#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
# coding: utf-8
#
# Links movie descriptions to media files in the movie database.
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
#   V1.0.1 2012-08-13


import re, sys, os.path
import MySQLdb
from moviedb import config, utils, version


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
    print "Links movie descriptions to media files in the movie database."
    print ""
    print "Usage:"
    print "  "+my_name+" [options]"
    print ""
    print "Options:"
    print "  -v          Verbose mode: Display additional messages."
    print "  -vm         Verbose mode: Display additional messages on matching movie file and movie description."
    print "  -h, --help  Display this help text."
    print ""
    print "Movie database:"
    print "  MySQL host: "+config.mysql_host+" (default port 3306)"
    print "  MySQL user: "+config.mysql_user+" (no password)"
    print "  MySQL database: "+config.mysql_db
    print ""

    return


#------------------------------------------------------------------------------
def SetIdMovieInMedium(new_idMovie, idMedium, movie_dn):

    global num_errors, verbose_mode

    utils.Msg("Linking movie file to movie description: "+movie_dn, verbose_mode)

    sql = "UPDATE Medium SET idMovie = '"+str(new_idMovie)+"' WHERE idMedium = '"+str(idMedium)+"'"

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)

    medium_cursor.execute(sql)

    medium_cursor.close()

    movies_conn.commit()


#------------------------------------------------------------------------------
# main routine
#


num_errors = 0                  # global number of errors
verbose_mode = False            # verbose mode, controlled by -v option
verbosematching_mode = False    # verbose matching mode, controlled by -vm option

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
        elif arg == "-vm":
            verbosematching_mode = True
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
movies_conn = MySQLdb.connect( host=config.mysql_host, user=config.mysql_user,
                               db=config.mysql_db, use_unicode=True, charset='utf8')


# Retrieve all movie descriptions

_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute(u"SELECT * FROM Movie")
movie_rowlist = _cursor.fetchall()
_cursor.close()

utils.Msg("Found "+str(len(movie_rowlist))+" movie descriptions in movie database (Movie table)")


# Retrieve all movie files

_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute(u"SELECT * FROM Medium")
medium_rowlist = _cursor.fetchall()
_cursor.close()

utils.Msg("Found "+str(len(medium_rowlist))+" movie files in movie database (Medium table)")


movies_conn.commit()


utils.Msg("Linking movie files to movie descriptions in movie database ...")


# Build dictionaries for fast access during matching

movie_tn_y_dict = dict()        # dictionary of movies
                                # key: normalized title '#' release year
                                # value: index into movie_rowlist array (0-based)

movie_otn_y_dict = dict()       # dictionary of movies
                                # key: normalized original title '#' release year
                                # value: index into movie_rowlist array (0-based)

movie_stn_etn_y_dict = dict()   # dictionary of movies
                                # key: normalized series title '#' normalized episode title '#' release year
                                # value: index into movie_rowlist array (0-based)

movie_ostn_oetn_y_dict = dict() # dictionary of movies
                                # key: normalized original series title '#' normalized original episode title '#' release year
                                # value: index into movie_rowlist array (0-based)

movie_stn_tn_y_dict = dict()    # dictionary of movies
                                # key: normalized series title '#' normalized title '#' release year
                                # value: index into movie_rowlist array (0-based)

movie_ostn_otn_y_dict = dict()  # dictionary of movies
                                # key: normalized original series title '#' normalized original title '#' release year
                                # value: index into movie_rowlist array (0-based)

movie_tn_dict = dict()          # dictionary of movies
                                # key: normalized title
                                # value: tuple with indexes into movie_rowlist array (0-based)

movie_otn_dict = dict()         # dictionary of movies
                                # key: normalized original title
                                # value: tuple with indexes into movie_rowlist array (0-based)

movie_stn_etn_dict = dict()     # dictionary of movies
                                # key: normalized series title '#' normalized episode title
                                # value: tuple with indexes into movie_rowlist array (0-based)

movie_ostn_oetn_dict = dict()   # dictionary of movies
                                # key: normalized original series title '#' normalized original episode title
                                # value: tuple with indexes into movie_rowlist array (0-based)

movie_stn_tn_dict = dict()      # dictionary of movies
                                # key: normalized series title '#' normalized title
                                # value: tuple with indexes into movie_rowlist array (0-based)

movie_ostn_otn_dict = dict()    # dictionary of movies
                                # key: normalized original series title '#' normalized original title
                                # value: tuple with indexes into movie_rowlist array (0-based)

i = 0
for movie_row in movie_rowlist:

    title_normalized = utils.NormalizeTitle(movie_row["Title"])
    original_title_normalized = utils.NormalizeTitle(movie_row["OriginalTitle"])

    series_title_normalized = utils.NormalizeTitle(movie_row["SeriesTitle"])
    original_series_title_normalized = utils.NormalizeTitle(movie_row["OriginalSeriesTitle"])

    episode_title_normalized = utils.NormalizeTitle(movie_row["EpisodeTitle"])
    original_episode_title_normalized = utils.NormalizeTitle(movie_row["OriginalEpisodeTitle"])

    year = movie_row["ReleaseYear"]

    if year != None:

        tn_y_key = title_normalized + "#" + str(year)
        if tn_y_key not in movie_tn_y_dict:
            movie_tn_y_dict[tn_y_key] = i
        else:
            utils.ErrorMsg("More than one movie description with same normalized title "+repr(title_normalized)+" and year "+str(year), num_errors)

        if original_title_normalized != None:
            otn_y_key = original_title_normalized + "#" + str(year)
            if otn_y_key not in movie_otn_y_dict:
                movie_otn_y_dict[otn_y_key] = i
            else:
                utils.ErrorMsg("More than one movie description with same normalized original title "+repr(original_title_normalized)+" and year "+str(year), num_errors)

        if series_title_normalized != None and episode_title_normalized != None:
            stn_etn_y_key = series_title_normalized + "#" + episode_title_normalized + "#" + str(year)
            if stn_etn_y_key not in movie_stn_etn_y_dict:
                movie_stn_etn_y_dict[stn_etn_y_key] = i
            else:
                utils.ErrorMsg("More than one movie description with same normalized series title "+repr(series_title_normalized)+", normalized episode title "+repr(episode_title_normalized)+" and year "+str(year), num_errors)

        if original_series_title_normalized != None and original_episode_title_normalized != None:
            ostn_oetn_y_key = original_series_title_normalized + "#" + original_episode_title_normalized + "#" + str(year)
            if ostn_oetn_y_key not in movie_ostn_oetn_y_dict:
                movie_ostn_oetn_y_dict[ostn_oetn_y_key] = i
            else:
                utils.ErrorMsg("More than one movie description with same normalized original series title "+repr(original_series_title_normalized)+", normalized original episode title "+repr(original_episode_title_normalized)+" and year "+str(year), num_errors)

        if series_title_normalized != None and title_normalized != None:
            stn_tn_y_key = series_title_normalized + "#" + title_normalized + "#" + str(year)
            if stn_tn_y_key not in movie_stn_tn_y_dict:
                movie_stn_tn_y_dict[stn_tn_y_key] = i
            else:
                utils.ErrorMsg("More than one movie description with same normalized series title "+repr(series_title_normalized)+", normalized title "+repr(title_normalized)+" and year "+str(year), num_errors)

        if original_series_title_normalized != None and original_title_normalized != None:
            ostn_otn_y_key = original_series_title_normalized + "#" + original_title_normalized + "#" + str(year)
            if ostn_otn_y_key not in movie_ostn_otn_y_dict:
                movie_ostn_otn_y_dict[ostn_otn_y_key] = i
            else:
                utils.ErrorMsg("More than one movie description with same normalized original series title "+repr(original_series_title_normalized)+", normalized original title "+repr(original_title_normalized)+" and year "+str(year), num_errors)

    else:
        utils.ErrorMsg("Movie database inconsistency: Movie with id "+str(movie_row["idMovie"])+" has no release year: '"+movie_row["Title"]+"'", num_errors)

    # We still need to build the dictionaries without year, in case we get movie files without year

    tn_key = title_normalized
    if tn_key not in movie_tn_dict:
        movie_tn_dict[tn_key] = []
    movie_tn_dict[tn_key].append(i)

    if original_title_normalized != None:
        otn_key = original_title_normalized
        if otn_key not in movie_otn_dict:
            movie_otn_dict[otn_key] = []
        movie_otn_dict[otn_key].append(i)

    if series_title_normalized != None and episode_title_normalized != None:
        stn_etn_key = series_title_normalized + "#" + episode_title_normalized
        if stn_etn_key not in movie_stn_etn_dict:
            movie_stn_etn_dict[stn_etn_key] = []
        movie_stn_etn_dict[stn_etn_key].append(i)

    if original_series_title_normalized != None and original_episode_title_normalized != None:
        ostn_oetn_key = original_series_title_normalized + "#" + original_episode_title_normalized
        if ostn_oetn_key not in movie_ostn_oetn_dict:
            movie_ostn_oetn_dict[ostn_oetn_key] = []
        movie_ostn_oetn_dict[ostn_oetn_key].append(i)

    if series_title_normalized != None and title_normalized != None:
        stn_tn_key = series_title_normalized + "#" + title_normalized
        if stn_tn_key not in movie_stn_tn_dict:
            movie_stn_tn_dict[stn_tn_key] = []
        movie_stn_tn_dict[stn_tn_key].append(i)

    if original_series_title_normalized != None and original_title_normalized != None:
        ostn_otn_key = original_series_title_normalized + "#" + original_title_normalized
        if ostn_otn_key not in movie_ostn_otn_dict:
            movie_ostn_otn_dict[ostn_otn_key] = []
        movie_ostn_otn_dict[ostn_otn_key].append(i)

    i += 1


# Link the records in the Media table to the Movie table

for medium_row in medium_rowlist:

    title_normalized = utils.NormalizeTitle(medium_row["Title"])
    series_title_normalized = utils.NormalizeTitle(medium_row["SeriesTitle"])
    episode_title_normalized = utils.NormalizeTitle(medium_row["EpisodeTitle"])

    if verbosematching_mode:
        utils.Msg("Matching info: Trying to find matching movie description for movie file: "+repr(medium_row["FilePath"]))

    title = medium_row["Title"]
    year = medium_row["ReleaseYear"]

    movie_row = None

    if year != None:

        movie_dn = title + " (" + str(year) + ")"

        if series_title_normalized != None and episode_title_normalized != None:

            # Movie file has series and episode titles -> use them first, then try title

            stn_etn_y_key = series_title_normalized + "#" + episode_title_normalized + "#" + str(year)
            tn_y_key = title_normalized + "#" + str(year)

            if stn_etn_y_key in movie_stn_etn_y_dict:

                # Series and episode titles of movie file match series and episode titles of movie description

                movie_row = movie_rowlist[movie_stn_etn_y_dict[stn_etn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #1 with series/episode and with year: Series and episode titles of movie file match series and episode titles of movie description : Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif stn_etn_y_key in movie_ostn_oetn_y_dict:

                # Series and episode titles of movie file match original series and episode titles of movie description

                movie_row = movie_rowlist[movie_ostn_oetn_y_dict[stn_etn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #2 with series/episode and with year: Series and episode titles of movie file match original series and episode titles of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif stn_etn_y_key in movie_stn_tn_y_dict:

                # Series and episode title of movie file match series title and normal title (in place of episode title) of movie description

                movie_row = movie_rowlist[movie_stn_tn_y_dict[stn_etn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #3 with series/episode and with year: Series and episode titles of movie file match series title and normal title (in place of episode title) of movie description : Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif stn_etn_y_key in movie_ostn_otn_y_dict:

                # Series and episode titles of movie file match original series title and original normal title (in place of episode title) of movie description

                movie_row = movie_rowlist[movie_ostn_otn_y_dict[stn_etn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #4 with series/episode and with year: Series and episode titles of movie file match original series title and original normal title (in place of episode title) of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif tn_y_key in movie_tn_y_dict:

                # Title of movie file matches title of movie description

                movie_row = movie_rowlist[movie_tn_y_dict[tn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #5 with series/episode and with year: Title of movie file matches title of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif tn_y_key in movie_otn_y_dict:

                # Title of movie file matches original title of movie description

                movie_row = movie_rowlist[movie_otn_y_dict[tn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #6 with series/episode and with year: Title of movie file matches original title of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            else:
                if verbosematching_mode:
                    utils.Msg("Matching info: No match with series/episode and with year")

        elif series_title_normalized != None and episode_title_normalized == None:

            # Movie file has series title but no episode title -> use series title as title, then try title

            stn_tn_y_key = series_title_normalized + "#" + title_normalized + "#" + str(year)
            stn_y_key = series_title_normalized + "#" + str(year)
            tn_y_key = title_normalized + "#" + str(year)

            if stn_tn_y_key in movie_stn_tn_y_dict:

                # Series title and normal title of movie file match series title and normal title (in place of episode title) of movie description

                movie_row = movie_rowlist[movie_stn_tn_y_dict[stn_tn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #1 with series title, without episode and with year: Series title and normal title of movie file match series title and normal title (in place of episode title) of movie description : Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif stn_tn_y_key in movie_ostn_otn_y_dict:

                # Series title and normal title of movie file match original series title and original title (in place of episode title) of movie description

                movie_row = movie_rowlist[movie_ostn_otn_y_dict[stn_tn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #2 with series title, without episode and with year: Series title and normal title of movie file match original series title and original title (in place of episode title) of movie description : Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif stn_y_key in movie_tn_y_dict:

                # Series title of movie file matches title of movie description

                movie_row = movie_rowlist[movie_tn_y_dict[stn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #3 with series title, without episode and with year: Series title of movie file matches title of movie description : Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif stn_y_key in movie_otn_y_dict:

                # Series title of movie file matches original title of movie description

                movie_row = movie_rowlist[movie_otn_y_dict[stn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #4 with series title, without episode and with year: Series title of movie file matches original title of movie description : Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif tn_y_key in movie_tn_y_dict:

                # Title of movie file matches title of movie description

                movie_row = movie_rowlist[movie_tn_y_dict[tn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #5 with series title, without episode and with year: Title of movie file matches title of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif tn_y_key in movie_otn_y_dict:

                # Title of movie file matches original title of movie description

                movie_row = movie_rowlist[movie_otn_y_dict[tn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #6 with series title, without episode and with year: Title of movie file matches original title of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            else:
                if verbosematching_mode:
                    utils.Msg("Matching info: No match with series title, without episode and with year")

        else:

            # Movie file has no series and episode titles -> only try title

            tn_y_key = title_normalized + "#" + str(year)

            if tn_y_key in movie_tn_y_dict:

                # Title of movie file matches title of movie description

                movie_row = movie_rowlist[movie_tn_y_dict[tn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #1 with just title and with year: Title of movie file matches title of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif tn_y_key in movie_otn_y_dict:

                # Title of movie file matches original title of movie description

                movie_row = movie_rowlist[movie_otn_y_dict[tn_y_key]]

                if verbosematching_mode:
                    utils.Msg("Matching info: Try #2 with just title and with year: Title of movie file matches original title of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            else:
                if verbosematching_mode:
                    utils.Msg("Matching info: No match with just title and with year")
    else:

        # Movie file has no year. Try to match without year.

        movie_dn = title

        if series_title_normalized != None and episode_title_normalized != None:

            # Movie file has series and episode titles -> use them first, then try title

            stn_etn_key = series_title_normalized + "#" + episode_title_normalized
            tn_key = title_normalized

            if stn_etn_key in movie_stn_etn_dict:

                # Series and episode titles of movie file match series and episode titles of movie description

                i_list = movie_stn_etn_dict[stn_etn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #1 with series/episode and without year: Series and episode titles of movie file match series and episode titles of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by series and episode) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            elif stn_etn_key in movie_ostn_oetn_dict:

                # Series and episode titles of movie file match original series and episode titles of movie description

                i_list = movie_ostn_oetn_dict[stn_etn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #2 with series/episode and without year: Series and episode titles of movie file match original series and episode titles of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by original series and episode) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            elif stn_etn_key in movie_stn_tn_dict:

                # Series and episode titles of movie file match series title and normal title (in place of episode title) of movie description

                i_list = movie_stn_tn_dict[stn_etn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #3 with series/episode and without year: Series and episode titles of movie file match series title and normal title (in place of episode title) of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by series and title as episode) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            elif stn_etn_key in movie_ostn_otn_dict:

                # Series and episode titles of movie file match original series title and original normal title (in place of episode title) of movie description

                i_list = movie_ostn_otn_dict[stn_etn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #4 with series/episode and without year: Series and episode titles of movie file match original series title and original normal title (in place of episode title) of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by original series and title as episode) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            elif tn_key in movie_tn_dict:

                # Title of movie file matches title of movie description

                i_list = movie_tn_dict[tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #5 with series/episode and without year: Title of movie file matches title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by title) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            elif tn_key in movie_otn_dict:

                # Title of movie file matches original title of movie description

                i_list = movie_otn_dict[tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #6 with series/episode and without year: Title of movie file matches original title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by original title) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            else:
                if verbosematching_mode:
                    utils.Msg("Matching info: No match with series/episode and without year")

        elif series_title_normalized != None and episode_title_normalized == None:

            # Movie file has series title but no episode title -> use series title as title, then try title

            stn_tn_key = series_title_normalized + "#" + title_normalized
            stn_key = series_title_normalized
            tn_key = title_normalized

            if stn_tn_key in movie_stn_tn_dict:

                # Series title and normal title of movie file match series title and normal title of movie description

                i_list = movie_stn_tn_dict[stn_tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #1 with series title, without episode and without year: Series title and normal title of movie file match series title and normal title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by series and title) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            elif stn_tn_key in movie_ostn_otn_dict:

                # Original series title and original title of movie file match original series title and original title of movie description

                i_list = movie_ostn_otn_dict[stn_tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #2 with series title, without episode and without year: Original series title and original title of movie file match original series title and original title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by original series and title) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            elif stn_key in movie_tn_dict:

                # Series title of movie file matches title of movie description

                i_list = movie_tn_dict[stn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #3 with series title, without episode and without year: Series title of movie file matches title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by series vs. title) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            elif stn_key in movie_otn_dict:

                # Series title of movie file matches title of movie description

                i_list = movie_otn_dict[stn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #4 with series title, without episode and without year: Series title of movie file matches original title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by original series vs. title) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            elif tn_key in movie_tn_dict:

                # Title of movie file matches title of movie description

                i_list = movie_tn_dict[tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #5 with series title, without episode and without year: Title of movie file matches title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by title) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            elif tn_key in movie_otn_dict:

                # Title of movie file matches original title of movie description

                i_list = movie_otn_dict[tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #6 with series title, without episode and without year: Title of movie file matches original title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by original title) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            else:
                if verbosematching_mode:
                    utils.Msg("Matching info: No match with series title, without episode and with year")

        else:

            # Movie file has no series and episode titles -> only try title

            tn_key = title_normalized

            if tn_key in movie_tn_dict:

                # Title of movie file matches title of movie description

                i_list = movie_tn_dict[tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #1 with just title and without year: Title of movie file matches title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by title) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            elif tn_key in movie_otn_dict:

                # Title of movie file matches original title of movie description

                i_list = movie_otn_dict[tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]

                    if verbosematching_mode:
                        utils.Msg("Matching info: Try #2 with just title and without year: Title of movie file matches original title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))

                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    utils.ErrorMsg("Skipping movie file without release year that matches (by original title) more than one movie description: "+repr(medium_row["FilePath"]), num_errors)

            else:
                if verbosematching_mode:
                    utils.Msg("Matching info: No match with just title and without year")


if num_errors > 0:
    utils.ErrorMsg("Finished with "+str(num_errors)+" errors.")
    exit(12)
else:
    utils.Msg("Success.")
    exit(0)
