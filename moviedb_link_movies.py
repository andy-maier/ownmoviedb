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
#   V1.2.1 2012-09-04
#     Improved algorithm to match movie files and movie descriptions.
#   V1.2.2 2012-09-05
#     Changed matching algorithm to consider episode ids "Teil" and "Part" as part of a mini-series
#     whose movie description is for the entire mini-series (and not per episode).


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
    print "Links media files to movie descriptions in the movie database."
    print ""
    print "Usage:"
    print "  "+my_name+" [options]"
    print ""
    print "Options:"
    print "  -r          Reset (unlink) all links before linking again."
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
def SetMovieLinkInMedium(movie_row, medium_row):

    global num_errors, verbose_mode

    utils.Msg("Linking movie file '"+os.path.basename(medium_row["FilePath"])+"'"+\
              " to movie description '"+movie_row["Title"]+" ("+str(movie_row["ReleaseYear"])+")'",
              verbose_mode)

    sql = "UPDATE Medium SET idMovie = '"+str(movie_row["idMovie"])+"'"+\
          " WHERE idMedium = '"+str(medium_row["idMedium"])+"'"

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)
    medium_cursor.execute(sql)
    medium_cursor.close()
    movies_conn.commit()


#------------------------------------------------------------------------------
def ResetMovieLinksInMedium():

    global num_errors, verbose_mode

    utils.Msg("Resetting all links of movie files to movie descriptions.", verbose_mode)

    sql = "UPDATE Medium SET idMovie = NULL WHERE idMovie IS NOT NULL"

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)
    medium_cursor.execute(sql)
    medium_cursor.close()
    movies_conn.commit()


#------------------------------------------------------------------------------
def MatchDictAndLink(medium_row, movie_dict_key, movie_dict, match_desc):

    global num_errors, verbosematching_mode

    movie_row = None

    if movie_dict_key in movie_dict:

        movie_dict_value = movie_dict[movie_dict_key]
        if type(movie_dict_value) == list:
            i_list = movie_dict_value
            if len(i_list) == 1:
                i = i_list[0]
            else:  # more than one matching movie
                _txt = ""
                for _i in i_list:
                    _movie_row = movie_rowlist[_i]
                    _txt += "  movie description "+str(_movie_row["idMovie"])+": "+\
                            "'"+_movie_row["Title"]+" ("+str(_movie_row["ReleaseYear"])+")'\n"
                utils.ErrorMsg("Not linking movie file that matches more than one movie description by "+match_desc+"\n"+\
                               "  movie file: '"+os.path.basename(medium_row["FilePath"])+"'\n"+\
                               _txt, num_errors)
                i = None
        else:
            i = movie_dict_value
            
        if i != None:
            movie_row = movie_rowlist[i]
            if verbosematching_mode:
                utils.Msg("  Found movie description "+str(movie_row["idMovie"])+" by matching "+match_desc)
            if medium_row["idMovie"] != movie_row["idMovie"]:
                SetMovieLinkInMedium(movie_row, medium_row)
            #else:
            #    print "Debug: movie id: "+str(movie_row["idMovie"])+", movie id in medium: "+str(medium_row["idMovie"])
    else:
        if verbosematching_mode:
            utils.Msg("  No movie description found by matching "+match_desc)

    return movie_row


#------------------------------------------------------------------------------
# main routine
#


num_errors = 0                  # global number of errors
verbose_mode = False            # verbose mode, controlled by -v option
verbosematching_mode = False    # verbose matching mode, controlled by -vm option
reset = False                   # reset links before linking, controlled by -r option

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
        elif arg == "-r":
            reset = True
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


if reset:
    ResetMovieLinksInMedium()

# Retrieve all movie descriptions

_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute(u"SELECT * FROM Movie")
movie_rowlist = _cursor.fetchall()
_cursor.close()

utils.Msg("Found "+str(len(movie_rowlist))+" movie descriptions in movie database.")


# Retrieve all movie files

_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute(u"SELECT * FROM Medium")
medium_rowlist = _cursor.fetchall()
_cursor.close()

utils.Msg("Found "+str(len(medium_rowlist))+" movie files in movie database.")

movies_conn.commit()


utils.Msg("Linking movie files in movie database to movie descriptions ...")


# Build dictionaries for fast access during matching

movie_tn_y_dict = dict()        # dictionary of movies
                                # key: normalized title '#' release year
                                # value: index into movie_rowlist array (0-based)

movie_otn_y_dict = dict()       # dictionary of movies
                                # key: normalized original title '#' release year
                                # value: index into movie_rowlist array (0-based)

#movie_stn_y_dict = dict()       # dictionary of movies
#                                # key: normalized series title '#' release year
#                                # value: index into movie_rowlist array (0-based)

#movie_ostn_y_dict = dict()      # dictionary of movies
#                                # key: normalized original series title '#' release year
#                                # value: index into movie_rowlist array (0-based)

movie_stn_ein_y_dict = dict()   # dictionary of movies
                                # key: normalized series title '#' normalized episode id '#' release year
                                # value: index into movie_rowlist array (0-based)

movie_ostn_ein_y_dict = dict()  # dictionary of movies
                                # key: normalized original series title '#' normalized episode id '#' release year
                                # value: index into movie_rowlist array (0-based)

movie_tn_dict = dict()          # dictionary of movies
                                # key: normalized title
                                # value: tuple with indexes into movie_rowlist array (0-based)

movie_otn_dict = dict()         # dictionary of movies
                                # key: normalized original title
                                # value: tuple with indexes into movie_rowlist array (0-based)

#movie_stn_dict = dict()         # dictionary of movies
#                                # key: normalized series title
#                                # value: tuple with indexes into movie_rowlist array (0-based)

#movie_ostn_dict = dict()        # dictionary of movies
#                                # key: normalized original series title
#                                # value: tuple with indexes into movie_rowlist array (0-based)

movie_stn_ein_dict = dict()     # dictionary of movies
                                # key: normalized series title '#' normalized episode id
                                # value: tuple with indexes into movie_rowlist array (0-based)

movie_ostn_ein_dict = dict()    # dictionary of movies
                                # key: normalized original series title '#' normalized episode id
                                # value: tuple with indexes into movie_rowlist array (0-based)


i = 0
for movie_row in movie_rowlist:

    title_normalized = utils.NormalizeTitle(movie_row["Title"])
    original_title_normalized = utils.NormalizeTitle(movie_row["OriginalTitle"])

    series_title_normalized = utils.NormalizeTitle(movie_row["SeriesTitle"])
    original_series_title_normalized = utils.NormalizeTitle(movie_row["OriginalSeriesTitle"])

    episode_id_normalized = utils.NormalizeTitle(movie_row["EpisodeId"])

    year = movie_row["ReleaseYear"]

    if year != None:

        tn_y_key = title_normalized + "#" + str(year)
        if tn_y_key not in movie_tn_y_dict:
            movie_tn_y_dict[tn_y_key] = i
        else:
            existing_movie_row = movie_rowlist[movie_tn_y_dict[tn_y_key]]
            utils.ErrorMsg("Inconsistency in table Movie: Two movie descriptions have matching title and year:\n"+\
                           "  idMovie "+str(movie_row["idMovie"])+": "+movie_row["Title"]+" ("+str(year)+")\n"+\
                           "  idMovie "+str(existing_movie_row["idMovie"])+": "+existing_movie_row["Title"]+" ("+str(year)+")", num_errors)

        if original_title_normalized != None:
            otn_y_key = original_title_normalized + "#" + str(year)
            if otn_y_key not in movie_otn_y_dict:
                movie_otn_y_dict[otn_y_key] = i
            else:
                existing_movie_row = movie_rowlist[movie_otn_y_dict[otn_y_key]]
                utils.ErrorMsg("Inconsistency in table Movie: Two movie descriptions have matching original title and year:\n"+\
                               "  idMovie "+str(movie_row["idMovie"])+": "+movie_row["Title"]+" ("+str(year)+")\n"+\
                               "  idMovie "+str(existing_movie_row["idMovie"])+": "+existing_movie_row["Title"]+" ("+str(year)+")", num_errors)

        #if series_title_normalized != None:
        #    stn_y_key = series_title_normalized + "#" + str(year)
        #    if stn_y_key not in movie_stn_y_dict:
        #        movie_stn_y_dict[stn_y_key] = i
        #    else:
        #        existing_movie_row = movie_rowlist[movie_stn_y_dict[stn_y_key]]
        #        utils.ErrorMsg("Inconsistency in table Movie: Two movie descriptions have matching series title and year:\n"+\
        #                       "  idMovie "+str(movie_row["idMovie"])+": "+movie_row["Title"]+" ("+str(year)+")\n"+\
        #                       "  idMovie "+str(existing_movie_row["idMovie"])+": "+existing_movie_row["Title"]+" ("+str(year)+")", num_errors)

        #if original_series_title_normalized != None:
        #    ostn_y_key = original_series_title_normalized + "#" + str(year)
        #    if ostn_y_key not in movie_ostn_y_dict:
        #        movie_ostn_y_dict[ostn_y_key] = i
        #    else:
        #        existing_movie_row = movie_rowlist[movie_ostn_y_dict[ostn_y_key]]
        #        utils.ErrorMsg("Inconsistency in table Movie: Two movie descriptions have matching original series title and year:\n"+\
        #                       "  idMovie "+str(movie_row["idMovie"])+": "+movie_row["Title"]+" ("+str(year)+")\n"+\
        #                       "  idMovie "+str(existing_movie_row["idMovie"])+": "+existing_movie_row["Title"]+" ("+str(year)+")", num_errors)

        if series_title_normalized != None and episode_id_normalized != None:
            stn_ein_y_key = series_title_normalized + "#" + episode_id_normalized + "#" + str(year)
            if stn_ein_y_key not in movie_stn_ein_y_dict:
                movie_stn_ein_y_dict[stn_ein_y_key] = i
            else:
                existing_movie_row = movie_rowlist[movie_stn_ein_y_dict[stn_ein_y_key]]
                utils.ErrorMsg("Inconsistency in table Movie: Two movie descriptions have matching series title, episode id and year:\n"+\
                               "  idMovie "+str(movie_row["idMovie"])+": "+movie_row["Title"]+" ("+str(year)+")\n"+\
                               "  idMovie "+str(existing_movie_row["idMovie"])+": "+existing_movie_row["Title"]+" ("+str(year)+")", num_errors)

        if original_series_title_normalized != None and episode_id_normalized != None:
            ostn_ein_y_key = original_series_title_normalized + "#" + episode_id_normalized + "#" + str(year)
            if ostn_ein_y_key not in movie_ostn_ein_y_dict:
                movie_ostn_ein_y_dict[ostn_ein_y_key] = i
            else:
                existing_movie_row = movie_rowlist[movie_ostn_ein_y_dict[ostn_ein_y_key]]
                utils.ErrorMsg("Inconsistency in table Movie: Two movie descriptions have matching original series title, episode id and year:\n"+\
                               "  idMovie "+str(movie_row["idMovie"])+": "+movie_row["Title"]+" ("+str(year)+")\n"+\
                               "  idMovie "+str(existing_movie_row["idMovie"])+": "+existing_movie_row["Title"]+" ("+str(year)+")", num_errors)

    else:
        utils.ErrorMsg("Inconsistency in table Movie: Movie description without release year:\n"+\
                       "  idMovie "+str(movie_row["idMovie"])+": "+movie_row["Title"], num_errors)

    # We still need to build the dictionaries without year, in case we get movie files without year

    tn_key = title_normalized
    if tn_key not in movie_tn_dict:
        movie_tn_dict[tn_key] = list()
    movie_tn_dict[tn_key].append(i)

    if original_title_normalized != None:
        otn_key = original_title_normalized
        if otn_key not in movie_otn_dict:
            movie_otn_dict[otn_key] = list()
        movie_otn_dict[otn_key].append(i)

    #if series_title_normalized != None:
    #    stn_key = series_title_normalized
    #    if stn_key not in movie_stn_dict:
    #        movie_stn_dict[stn_key] = list()
    #    movie_stn_dict[stn_key].append(i)

    #if original_series_title_normalized != None:
    #    ostn_key = original_series_title_normalized
    #    if ostn_key not in movie_ostn_dict:
    #        movie_ostn_dict[ostn_key] = list()
    #    movie_ostn_dict[ostn_key].append(i)

    if series_title_normalized != None and episode_id_normalized != None:
        stn_ein_key = series_title_normalized + "#" + episode_id_normalized
        if stn_ein_key not in movie_stn_ein_dict:
            movie_stn_ein_dict[stn_ein_key] = list()
        movie_stn_ein_dict[stn_ein_key].append(i)

    if original_series_title_normalized != None and episode_id_normalized != None:
        ostn_ein_key = original_series_title_normalized + "#" + episode_id_normalized
        if ostn_ein_key not in movie_ostn_ein_dict:
            movie_ostn_ein_dict[ostn_ein_key] = list()
        movie_ostn_ein_dict[ostn_ein_key].append(i)

    i += 1


# Link the records in the Media table to the Movie table

for medium_row in medium_rowlist:

    if verbosematching_mode:
        utils.Msg("Searching movie description for movie file '"+os.path.basename(medium_row["FilePath"])+"'")

    year = medium_row["ReleaseYear"]
    title = medium_row["Title"]
    series_title = medium_row["SeriesTitle"]
    episode_id = medium_row["EpisodeId"]

    title_normalized = utils.NormalizeTitle(title)
    series_title_normalized = utils.NormalizeTitle(series_title)
    episode_id_normalized = utils.NormalizeTitle(episode_id)


    movie_row = None

    if year != None:

        movie_dn = title + " (" + str(year) + ")"

        if utils.HasEpisodeDescription(series_title, episode_id):
            # Movie file is expected to have an episode-based movie description
            
            stn_ein_y_key = series_title_normalized + "#" + episode_id_normalized + "#" + str(year)

            if movie_row == None:
                movie_row = MatchDictAndLink(medium_row, stn_ein_y_key, movie_stn_ein_y_dict,
                                             "file series title, episode id, year with "+\
                                             "description series title, episode id, year")

            if movie_row == None:
                movie_row = MatchDictAndLink(medium_row, stn_ein_y_key, movie_ostn_ein_y_dict,
                                             "file series title, episode id, year with "+\
                                             "description original series title, episode id, year")

        else:
            # Movie file is not expected to have an episode-based movie description

            if series_title_normalized != None:
                # Movie is a mini-series ("Teil", "part")
                
                stn_y_key = series_title_normalized + "#" + str(year)

                if movie_row == None:
                    movie_row = MatchDictAndLink(medium_row, stn_y_key, movie_tn_y_dict,
                                                 "file series title, year with "+\
                                                 "description title, year")

                if movie_row == None:
                    movie_row = MatchDictAndLink(medium_row, stn_y_key, movie_otn_y_dict,
                                                 "file series title, year with "+\
                                                 "description original title, year")

            # We test file title against description title to catch cases where description title contains "Teil"
            
            tn_y_key = title_normalized + "#" + str(year)

            if movie_row == None:
                movie_row = MatchDictAndLink(medium_row, tn_y_key, movie_tn_y_dict,
                                             "file title, year with "+\
                                             "description title, year")

            if movie_row == None:
                movie_row = MatchDictAndLink(medium_row, tn_y_key, movie_otn_y_dict,
                                             "file title, year with "+\
                                             "description original title, year")

    else:  # Movie file has no year

        if utils.HasEpisodeDescription(series_title, episode_id):
            # Movie file is expected to have an episode-based movie description

            stn_ein_key = series_title_normalized + "#" + episode_id_normalized

            if movie_row == None:
                movie_row = MatchDictAndLink(medium_row, stn_ein_key, movie_stn_ein_dict,
                                             "file series title, episode id with "+\
                                             "description series title, episode id")

            if movie_row == None:
                movie_row = MatchDictAndLink(medium_row, stn_ein_key, movie_ostn_ein_dict,
                                             "file series title, episode id with "+\
                                             "description original series title, episode id")

        else:
            # Movie file is not expected to have an episode-based movie description

            if series_title_normalized != None:
                # Movie file is a mini-series ("Teil", "part")

                stn_key = series_title_normalized

                if movie_row == None:
                    movie_row = MatchDictAndLink(medium_row, stn_key, movie_tn_dict,
                                                 "file series title with "+\
                                                 "description title")

                if movie_row == None:
                    movie_row = MatchDictAndLink(medium_row, stn_key, movie_otn_dict,
                                                 "file series title with "+\
                                                 "description original title")

            # We test file title against description title to catch cases where description title contains "Teil"
            
            tn_key = title_normalized

            if movie_row == None:
                movie_row = MatchDictAndLink(medium_row, tn_key, movie_tn_dict,
                                             "file title with "+\
                                             "description title")

            if movie_row == None:
                movie_row = MatchDictAndLink(medium_row, tn_key, movie_otn_dict,
                                             "file title with "+\
                                             "description original title")

    if movie_row == None:
        if verbosematching_mode:
            utils.Msg("No movie description found for movie file '"+os.path.basename(medium_row["FilePath"])+"'")
        

if num_errors > 0:
    utils.ErrorMsg("Finished with "+str(num_errors)+" errors.")
    exit(12)
else:
    utils.Msg("Success.")
    exit(0)
