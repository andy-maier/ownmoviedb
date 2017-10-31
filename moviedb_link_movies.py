#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Links movie descriptions to media files in the movie database.
Usage see below in Usage(), or invoke with '-h' or '--help'.
"""


import sys
import os.path

import MySQLdb

from moviedb import config, utils, version


MY_NAME = os.path.basename(os.path.splitext(sys.argv[0])[0])

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
    print "  "+MY_NAME+" [options]"
    print ""
    print "Options:"
    print "  -r          Reset (unlink) all links before linking again."
    print "  -v          Verbose mode: Display additional messages."
    print "  -vm         Verbose mode: Display additional messages on matching movie file and movie description."
    print "  -h, --help  Display this help text."
    print ""
    print "Movie database:"
    print "  MySQL host: "+config.MYSQL_HOST+" (default port 3306)"
    print "  MySQL user: "+config.MYSQL_USER+" (no password)"
    print "  MySQL database: "+config.MYSQL_DB
    print ""

    return


#------------------------------------------------------------------------------
def SetMovieLinkInMedium(movies_conn, movie_row, medium_row):

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
def ResetMovieLinksInMedium(movies_conn):

    global num_errors, verbose_mode

    utils.Msg("Resetting all links of movie files to movie descriptions.", verbose_mode)

    sql = "UPDATE Medium SET idMovie = NULL WHERE idMovie IS NOT NULL"

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)
    medium_cursor.execute(sql)
    medium_cursor.close()
    movies_conn.commit()


#------------------------------------------------------------------------------
def MatchDictAndLink(movies_conn, medium_row, movie_rowlist, movie_dict_key, movie_dict, match_desc):

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
                SetMovieLinkInMedium(movies_conn, movie_row, medium_row)
            #else:
            #    print "Debug: movie id: "+str(movie_row["idMovie"])+", movie id in medium: "+str(medium_row["idMovie"])
    else:
        if verbosematching_mode:
            utils.Msg("  No movie description found by matching "+match_desc)

    return movie_row


def main():
    global num_errors, verbose_mode, verbosematching_mode

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

    utils.Msg( MY_NAME+" Version "+version.__version__)


    # Connection to movie database
    movies_conn = MySQLdb.connect( host=config.MYSQL_HOST, user=config.MYSQL_USER,
                                   db=config.MYSQL_DB, use_unicode=True, charset='utf8')


    if reset:
        ResetMovieLinksInMedium(movies_conn)

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

    movie_stn_ein_y_dict = dict()   # dictionary of movies
                                    # key: normalized series title '#' normalized episode id '#' release year
                                    # value: index into movie_rowlist array (0-based)

    movie_ostn_ein_y_dict = dict()  # dictionary of movies
                                    # key: normalized original series title '#' normalized episode id '#' release year
                                    # value: index into movie_rowlist array (0-based)

    movie_stn_etn_y_dict = dict()   # dictionary of movies
                                    # key: normalized series title '#' normalized episode title '#' release year
                                    # value: tuple with indexes into movie_rowlist array (0-based)

    movie_ostn_oetn_y_dict = dict() # dictionary of movies
                                    # key: normalized original series title '#' normalized original episode title '#' release year
                                    # value: tuple with indexes into movie_rowlist array (0-based)

    movie_tn_dict = dict()          # dictionary of movies
                                    # key: normalized title
                                    # value: tuple with indexes into movie_rowlist array (0-based)

    movie_otn_dict = dict()         # dictionary of movies
                                    # key: normalized original title
                                    # value: tuple with indexes into movie_rowlist array (0-based)

    movie_stn_ein_dict = dict()     # dictionary of movies
                                    # key: normalized series title '#' normalized episode id
                                    # value: tuple with indexes into movie_rowlist array (0-based)

    movie_ostn_ein_dict = dict()    # dictionary of movies
                                    # key: normalized original series title '#' normalized episode id
                                    # value: tuple with indexes into movie_rowlist array (0-based)

    movie_stn_etn_dict = dict()     # dictionary of movies
                                    # key: normalized series title '#' normalized episode title
                                    # value: tuple with indexes into movie_rowlist array (0-based)

    movie_ostn_oetn_dict = dict()   # dictionary of movies
                                    # key: normalized original series title '#' normalized original episode title
                                    # value: tuple with indexes into movie_rowlist array (0-based)


    i = 0
    for movie_row in movie_rowlist:

        title_normalized = utils.NormalizeTitle(movie_row["Title"])
        original_title_normalized = utils.NormalizeTitle(movie_row["OriginalTitle"])

        series_title_normalized = utils.NormalizeTitle(movie_row["SeriesTitle"])
        original_series_title_normalized = utils.NormalizeTitle(movie_row["OriginalSeriesTitle"])

        episode_id_normalized = utils.NormalizeTitle(movie_row["EpisodeId"])

        episode_title_normalized = utils.NormalizeTitle(movie_row["EpisodeTitle"])
        original_episode_title_normalized = utils.NormalizeTitle(movie_row["OriginalEpisodeTitle"])

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

            if series_title_normalized != None and episode_title_normalized != None:
                stn_etn_y_key = series_title_normalized + "#" + episode_title_normalized + "#" + str(year)
                if stn_etn_y_key not in movie_stn_etn_y_dict:
                    movie_stn_etn_y_dict[stn_etn_y_key] = list()
                movie_stn_etn_y_dict[stn_etn_y_key].append(i)

            if original_series_title_normalized != None and original_episode_title_normalized != None:
                ostn_oetn_y_key = original_series_title_normalized + "#" + original_episode_title_normalized + "#" + str(year)
                if ostn_oetn_y_key not in movie_ostn_oetn_y_dict:
                    movie_ostn_oetn_y_dict[ostn_oetn_y_key] = list()
                movie_ostn_oetn_y_dict[ostn_oetn_y_key].append(i)

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

        if series_title_normalized != None and episode_title_normalized != None:
            stn_etn_key = series_title_normalized + "#" + episode_title_normalized
            if stn_etn_key not in movie_stn_etn_dict:
                movie_stn_etn_dict[stn_etn_key] = list()
            movie_stn_etn_dict[stn_etn_key].append(i)

        if original_series_title_normalized != None and original_episode_title_normalized != None:
            ostn_oetn_key = original_series_title_normalized + "#" + original_episode_title_normalized
            if ostn_oetn_key not in movie_ostn_oetn_dict:
                movie_ostn_oetn_dict[ostn_oetn_key] = list()
            movie_ostn_oetn_dict[ostn_oetn_key].append(i)

        i += 1


    # Link the records in the Media table to the Movie table

    for medium_row in medium_rowlist:

        if verbosematching_mode:
            utils.Msg("Searching movie description for movie file '"+os.path.basename(medium_row["FilePath"])+"'")

        year = medium_row["ReleaseYear"]
        title = medium_row["Title"]
        series_title = medium_row["SeriesTitle"]
        episode_id = medium_row["EpisodeId"]
        episode_title = medium_row["EpisodeTitle"]

        title_normalized = utils.NormalizeTitle(title)
        series_title_normalized = utils.NormalizeTitle(series_title)
        episode_id_normalized = utils.NormalizeTitle(episode_id)
        episode_title_normalized = utils.NormalizeTitle(episode_title)


        movie_row = None

        if year != None:

            # movie_dn = title + " (" + str(year) + ")"

            if utils.HasEpisodeDescription(series_title, episode_id):
                # Movie file is expected to have an episode-based movie description

                stn_ein_y_key = series_title_normalized + "#" + episode_id_normalized + "#" + str(year)

                if movie_row == None:
                    movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, stn_ein_y_key, movie_stn_ein_y_dict,
                                                 ("file series title '%s', episode id '%s', year %d with "\
                                                 "description series title, episode id, year" % (series_title, episode_id, year)))

                if movie_row == None:
                    movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, stn_ein_y_key, movie_ostn_ein_y_dict,
                                                 ("file series title '%s', episode id '%s', year %d with "\
                                                 "description original series title, episode id, year" % (series_title, episode_id, year)))

                if episode_title_normalized is not None:

                    stn_etn_y_key = series_title_normalized + "#" + episode_title_normalized + "#" + str(year)

                    if movie_row == None:
                        movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, stn_etn_y_key, movie_stn_etn_y_dict,
                                                     ("file series title '%s', episode title '%s', year %d with "\
                                                     "description series title, episode title, year" % (series_title, episode_title, year)))

                    if movie_row == None:
                        movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, stn_etn_y_key, movie_ostn_oetn_y_dict,
                                                     ("file series title '%s', episode title '%s', year %d with "\
                                                     "description original series title, original episode title, year" % (series_title, episode_title, year)))

                    tn_y_key = series_title_normalized + " " + episode_title_normalized + "#" + str(year)

                    if movie_row == None:
                        movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, tn_y_key, movie_tn_y_dict,
                                                     ("file series title '%s' + episode title '%s', year %d with "\
                                                     "description title, year" % (series_title, episode_title, year)))

                    if movie_row == None:
                        movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, tn_y_key, movie_otn_y_dict,
                                                     ("file series title '%s' + episode title '%s', year %d with "\
                                                     "description original title, year" % (series_title, episode_title, year)))

            else:
                # Movie file is not expected to have an episode-based movie description

                if series_title_normalized != None:
                    # Movie is a mini-series ("Teil", "part")

                    stn_y_key = series_title_normalized + "#" + str(year)

                    if movie_row == None:
                        movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, stn_y_key, movie_tn_y_dict,
                                                     ("file series title '%s', year %d with "\
                                                     "description title, year" % (series_title, year)))

                    if movie_row == None:
                        movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, stn_y_key, movie_otn_y_dict,
                                                     ("file series title '%s', year %d with "\
                                                     "description original title, year" % (series_title, year)))

                # We test file title against description title to catch cases where description title contains "Teil"

                tn_y_key = title_normalized + "#" + str(year)

                if movie_row == None:
                    movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, tn_y_key, movie_tn_y_dict,
                                                 ("file title '%s', year %d with "\
                                                 "description title, year" % (title, year)))

                if movie_row == None:
                    movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, tn_y_key, movie_otn_y_dict,
                                                 ("file title '%s', year %d with "\
                                                 "description original title, year" % (title, year)))

        else:  # Movie file has no year

            if utils.HasEpisodeDescription(series_title, episode_id):
                # Movie file is expected to have an episode-based movie description

                stn_ein_key = series_title_normalized + "#" + episode_id_normalized

                if movie_row == None:
                    movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, stn_ein_key, movie_stn_ein_dict,
                                                 ("file series title '%s', episode id '%s' with "\
                                                 "description series title, episode id" % (series_title, episode_id)))

                if movie_row == None:
                    movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, stn_ein_key, movie_ostn_ein_dict,
                                                 ("file series title '%s', episode id '%s' with "\
                                                 "description original series title, episode id" % (series_title, episode_id)))

                if episode_title_normalized is not None:

                    stn_etn_key = series_title_normalized + "#" + episode_title_normalized

                    if movie_row == None:
                        movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, stn_etn_key, movie_stn_etn_dict,
                                                     ("file series title '%s', episode title '%s' with "\
                                                     "description series title, episode title" % (series_title, episode_title)))

                    if movie_row == None:
                        movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, stn_etn_key, movie_ostn_oetn_dict,
                                                     ("file series title '%s', episode title '%s' with "\
                                                     "description original series title, original episode title" % (series_title, episode_title)))

                    tn_key = series_title_normalized + " " + episode_title_normalized

                    if movie_row == None:
                        movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, tn_key, movie_tn_dict,
                                                     ("file series title '%s' + episode title '%s' with "\
                                                     "description title, year" % (series_title, episode_title)))

                    if movie_row == None:
                        movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, tn_key, movie_otn_dict,
                                                     ("file series title '%s' + episode title '%s' with "\
                                                     "description original title, year" % (series_title, episode_title)))

            else:
                # Movie file is not expected to have an episode-based movie description

                if series_title_normalized != None:
                    # Movie file is a mini-series ("Teil", "part")

                    stn_key = series_title_normalized

                    if movie_row == None:
                        movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, stn_key, movie_tn_dict,
                                                     ("file series title '%s' with "\
                                                     "description title" % (series_title)))

                    if movie_row == None:
                        movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, stn_key, movie_otn_dict,
                                                     ("file series title '%s' with "\
                                                     "description original title" % (series_title)))

                # We test file title against description title to catch cases where description title contains "Teil"

                tn_key = title_normalized

                if movie_row == None:
                    movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, tn_key, movie_tn_dict,
                                                 ("file title '%s' with "\
                                                 "description title" % (title)))

                if movie_row == None:
                    movie_row = MatchDictAndLink(movies_conn, medium_row, movie_rowlist, tn_key, movie_otn_dict,
                                                 ("file title '%s' with "\
                                                 "description original title" % (title)))

        if movie_row == None:
            if verbosematching_mode:
                utils.Msg("No movie description found for movie file '"+os.path.basename(medium_row["FilePath"])+"'")


    if num_errors > 0:
        utils.ErrorMsg("Finished with "+str(num_errors)+" errors.")
        return 12
    else:
        utils.Msg("Success.")
        return 0

if __name__ == '__main__':
    exit(main())
