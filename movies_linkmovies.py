#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
# coding: utf-8
#
# Usage see below in Usage(), or invoke with '-?' or '--help'.
#
# Supported platforms:
#   Runs on any OS platform that has Python 2.7.
#   Tested on Windows XP.
#
# Prerequisites:
#   1. Python 2.7, available from http://www.python.org
#
# Debug:
#   import pdb; pdb.set_trace()
#

my_name = "movies_linkmovies"
my_version = "1.0.1"

import re, sys
import MySQLdb
from movies_conf import *


num_errors = 0                  # global number of errors
quiet_mode = True               # quiet mode, controlled by -v option
verbosematching_mode = False    # verbose matching mode, controlled by -vm option

#------------------------------------------------------------------------------
def Usage ():
    """Print the command usage to stdout.
       Input:
         n/a
       Return:
         void.
    """

    print ""
    print "Links movie descriptions and media records in the movies database."
    print ""
    print "Usage:"
    print "  "+my_name+" [options]"
    print ""
    print "Options:"
    print "  -v          Verbose mode: Display additional messages."
    print "  -vm         Verbose mode: Display additional messages on matching movie file and movie description."
    print ""
    print "MySQL server:"
    print "  host: "+mysql_host+" (default port 3306)"
    print "  user: "+mysql_user+" (no password)"
    print "  database: "+mysql_db
    print ""

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

# Translation table for normalizing strings for comparison
normalize_utrans_table = [
    (228, 'ae'),  # a umlaut
    (246, 'oe'),  # o umlaut
    (252, 'ue'),  # u umlaut
    (223, 'ss'),  # german sharp s
    (196, 'Ae'),  # A umlaut
    (214, 'Oe'),  # O umlaut
    (220, 'Ue'),  # U umlaut
    (225, 'a'),   # a acute
    (224, 'a'),   # a grave
    (226, 'a'),   # a circumflex
    (229, 'a'),   # a ring
    (231, 'c'),   # c cedil
    (233, 'e'),   # e acute
    (232, 'e'),   # e grave
    (234, 'e'),   # e circumflex
    (237, 'i'),   # i acute
    (236, 'i'),   # i grave
    (238, 'i'),   # i circumflex
    (241, 'n'),   # n tilde
    (243, 'o'),   # o acute
    (242, 'o'),   # o grave
    (244, 'o'),   # o circumflex
    (250, 'u'),   # u acute
    (249, 'u'),   # u grave
    (251, 'u'),   # u circumflex
    (193, 'A'),   # A acute
    (192, 'A'),   # A grave
    (194, 'A'),   # A circumflex
    (197, 'A'),   # A ring
    (199, 'C'),   # C cedil
    (201, 'E'),   # E acute
    (200, 'E'),   # E grave
    (202, 'E'),   # E circumflex
    (205, 'I'),   # I acute
    (204, 'I'),   # I grave
    (206, 'I'),   # I circumflex
    (209, 'N'),   # N tilde
    (211, 'O'),   # O acute
    (210, 'O'),   # O grave
    (212, 'O'),   # O circumflex
    (218, 'U'),   # U acute
    (217, 'U'),   # U grave
    (219, 'U'),   # U circumflex
    (32,  '  '),  # space (to handle ' aside of space)
    (33,  ' '),   # !
    (35,  ' '),   # #
    (36,  ' '),   # $
    (37,  ' '),   # %
    (38,  ' '),   # &
    (39,  ''),    # '
    (40,  ' '),   # (
    (41,  ' '),   # )
    (42,  ' '),   # *
    (43,  ' '),   # +
    (44,  ' '),   # ,
    (45,  ' '),   # -
    (46,  ' '),   # .
    (47,  ' '),   # /
    (58,  ' '),   # :
    (59,  ' '),   # ;
    (61,  ' '),   # =
    (63,  ' '),   # ?
    (64,  ' '),   # @
    (91,  ' '),   # [
    (93,  ' '),   # ]
    (95,  ' '),   # _
]

#------------------------------------------------------------------------------
def NormalizeTitle(title):
    # title is a unicode string

    ntitle = NormalizeString(StripSquareBrackets(title))

    return ntitle


#------------------------------------------------------------------------------
def NormalizeString(_str):
    # _str is a unicode string

    global normalize_utrans_table

    if _str == None:
        nstr = None
    else:
        nstr = _str
        for fm_ord,to_str in normalize_utrans_table:
            nstr = nstr.replace(unichr(fm_ord),to_str)
        nstr = nstr.lower()
        nstr = nstr.replace("  "," ")
        nstr = nstr.replace("  "," ")
        nstr = nstr.replace("  "," ")
        nstr = nstr.strip(" ")

    return nstr


#------------------------------------------------------------------------------
def StripSquareBrackets(movie_title):

    if movie_title == None:
        movie_title_stripped = None
    else:
        m = re.match("(.*)(\[.*\])(.*)",movie_title)
        if m:
            _tp1, _sb, _tp2 = m.groups()
            movie_title_stripped = (_tp1 + _tp2).replace(" , ",", ").replace("  "," ").strip(" ")
        else:
            movie_title_stripped = movie_title

    return movie_title_stripped


#------------------------------------------------------------------------------
def SqlLiteral(_str):
    # _str is a (unicode) string for use in a SQL literal

    nstr = _str
    nstr = nstr.replace("'","\\'")

    return nstr


#------------------------------------------------------------------------------
def SetIdMovieInMedium(new_idMovie, idMedium, movie_dn):

    Msg("Linking movie file to movie description: "+movie_dn)

    sql = "UPDATE Medium SET idMovie = '"+str(new_idMovie)+"' WHERE idMedium = '"+str(idMedium)+"'"
    # Msg("Debug: sql = "+sql)

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)

    medium_cursor.execute(sql)

    medium_cursor.close()

    movies_conn.commit()


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
        elif arg == "-v":
            quiet_mode = False
        elif arg == "-vm":
            verbosematching_mode = True
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


# Retrieve all movie descriptions

_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute(u"SELECT * FROM Movie")
movie_rowlist = _cursor.fetchall()
_cursor.close()

Msg("Found "+str(len(movie_rowlist))+" movie descriptions in movie database (Movie table)")


# Retrieve all movie files

_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute(u"SELECT * FROM Medium")
medium_rowlist = _cursor.fetchall()
_cursor.close()

Msg("Found "+str(len(medium_rowlist))+" movie files in movie database (Medium table)")


movies_conn.commit()


Msg("Linking movie files to movie descriptions in movie database ...")


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

    title_normalized = NormalizeTitle(movie_row["Title"])
    original_title_normalized = NormalizeTitle(movie_row["OriginalTitle"])

    series_title_normalized = NormalizeTitle(movie_row["SeriesTitle"])
    original_series_title_normalized = NormalizeTitle(movie_row["OriginalSeriesTitle"])

    episode_title_normalized = NormalizeTitle(movie_row["EpisodeTitle"])
    original_episode_title_normalized = NormalizeTitle(movie_row["OriginalEpisodeTitle"])

    year = movie_row["ReleaseYear"]

    if year != None:

        tn_y_key = title_normalized + "#" + str(year)
        if tn_y_key not in movie_tn_y_dict:
            movie_tn_y_dict[tn_y_key] = i
        else:
            ErrorMsg("More than one movie description with same normalized title "+repr(title_normalized)+" and year "+str(year))

        if original_title_normalized != None:
            otn_y_key = original_title_normalized + "#" + str(year)
            if otn_y_key not in movie_otn_y_dict:
                movie_otn_y_dict[otn_y_key] = i
            else:
                ErrorMsg("More than one movie description with same normalized original title "+repr(original_title_normalized)+" and year "+str(year))

        if series_title_normalized != None and episode_title_normalized != None:
            stn_etn_y_key = series_title_normalized + "#" + episode_title_normalized + "#" + str(year)
            if stn_etn_y_key not in movie_stn_etn_y_dict:
                movie_stn_etn_y_dict[stn_etn_y_key] = i
            else:
                ErrorMsg("More than one movie description with same normalized series title "+repr(series_title_normalized)+", normalized episode title "+repr(episode_title_normalized)+" and year "+str(year))

        if original_series_title_normalized != None and original_episode_title_normalized != None:
            ostn_oetn_y_key = original_series_title_normalized + "#" + original_episode_title_normalized + "#" + str(year)
            if ostn_oetn_y_key not in movie_ostn_oetn_y_dict:
                movie_ostn_oetn_y_dict[ostn_oetn_y_key] = i
            else:
                ErrorMsg("More than one movie description with same normalized original series title "+repr(original_series_title_normalized)+", normalized original episode title "+repr(original_episode_title_normalized)+" and year "+str(year))

        if series_title_normalized != None and title_normalized != None:
            stn_tn_y_key = series_title_normalized + "#" + title_normalized + "#" + str(year)
            if stn_tn_y_key not in movie_stn_tn_y_dict:
                movie_stn_tn_y_dict[stn_tn_y_key] = i
            else:
                ErrorMsg("More than one movie description with same normalized series title "+repr(series_title_normalized)+", normalized title "+repr(title_normalized)+" and year "+str(year))

        if original_series_title_normalized != None and original_title_normalized != None:
            ostn_otn_y_key = original_series_title_normalized + "#" + original_title_normalized + "#" + str(year)
            if ostn_otn_y_key not in movie_ostn_otn_y_dict:
                movie_ostn_otn_y_dict[ostn_otn_y_key] = i
            else:
                ErrorMsg("More than one movie description with same normalized original series title "+repr(original_series_title_normalized)+", normalized original title "+repr(original_title_normalized)+" and year "+str(year))

    else:
        ErrorMsg("Movie database inconsistency: Movie with id "+str(movie_row["idMovie"])+" has no release year: '"+movie_row["Title"]+"'")

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

    title_normalized = NormalizeTitle(medium_row["Title"])
    series_title_normalized = NormalizeTitle(medium_row["SeriesTitle"])
    episode_title_normalized = NormalizeTitle(medium_row["EpisodeTitle"])

    if verbosematching_mode:
        Msg("Matching info: Trying to find matching movie description for movie file: "+repr(medium_row["FilePath"]))

    title = medium_row["Title"]
    year = medium_row["ReleaseYear"]

    movie_row = None

    if year != None:

        movie_dn = title + " (" + str(year) + ")"

        if series_title_normalized != None and episode_title_normalized != None:

            # Movie file has series and episode titles -> use them first, then try title

            stn_etn_y_key = series_title_normalized + "#" + episode_title_normalized + "#" + str(year)
            tn_y_key = title_normalized + "#" + str(year)

            #if verbosematching_mode:
            #    Msg("Matching info: Debug: stn_etn_y_key = "+repr(stn_etn_y_key))
            #    Msg("Matching info: Debug: tn_y_key = "+repr(tn_y_key))

            if stn_etn_y_key in movie_stn_etn_y_dict:

                # Series and episode titles of movie file match series and episode titles of movie description

                movie_row = movie_rowlist[movie_stn_etn_y_dict[stn_etn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #1 with series/episode and with year: Series and episode titles of movie file match series and episode titles of movie description : Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif stn_etn_y_key in movie_ostn_oetn_y_dict:

                # Series and episode titles of movie file match original series and episode titles of movie description

                movie_row = movie_rowlist[movie_ostn_oetn_y_dict[stn_etn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #2 with series/episode and with year: Series and episode titles of movie file match original series and episode titles of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif stn_etn_y_key in movie_stn_tn_y_dict:

                # Series and episode title of movie file match series title and normal title (in place of episode title) of movie description

                movie_row = movie_rowlist[movie_stn_tn_y_dict[stn_etn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #3 with series/episode and with year: Series and episode titles of movie file match series title and normal title (in place of episode title) of movie description : Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif stn_etn_y_key in movie_ostn_otn_y_dict:

                # Series and episode titles of movie file match original series title and original normal title (in place of episode title) of movie description

                movie_row = movie_rowlist[movie_ostn_otn_y_dict[stn_etn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #4 with series/episode and with year: Series and episode titles of movie file match original series title and original normal title (in place of episode title) of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif tn_y_key in movie_tn_y_dict:

                # Title of movie file matches title of movie description

                movie_row = movie_rowlist[movie_tn_y_dict[tn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #5 with series/episode and with year: Title of movie file matches title of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif tn_y_key in movie_otn_y_dict:

                # Title of movie file matches original title of movie description

                movie_row = movie_rowlist[movie_otn_y_dict[tn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #6 with series/episode and with year: Title of movie file matches original title of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            else:
                if verbosematching_mode:
                    Msg("Matching info: No match with series/episode and with year")

        elif series_title_normalized != None and episode_title_normalized == None:

            # Movie file has series title but no episode title -> use series title as title, then try title

            stn_tn_y_key = series_title_normalized + "#" + title_normalized + "#" + str(year)
            stn_y_key = series_title_normalized + "#" + str(year)
            tn_y_key = title_normalized + "#" + str(year)

            #if verbosematching_mode:
            #    Msg("Matching info: Debug: stn_tn_y_key = "+repr(stn_tn_y_key))
            #    Msg("Matching info: Debug: stn_y_key = "+repr(stn_y_key))
            #    Msg("Matching info: Debug: tn_y_key = "+repr(tn_y_key))

            if stn_tn_y_key in movie_stn_tn_y_dict:

                # Series title and normal title of movie file match series title and normal title (in place of episode title) of movie description

                movie_row = movie_rowlist[movie_stn_tn_y_dict[stn_tn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #1 with series title, without episode and with year: Series title and normal title of movie file match series title and normal title (in place of episode title) of movie description : Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif stn_tn_y_key in movie_ostn_otn_y_dict:

                # Series title and normal title of movie file match original series title and original title (in place of episode title) of movie description

                movie_row = movie_rowlist[movie_ostn_otn_y_dict[stn_tn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #2 with series title, without episode and with year: Series title and normal title of movie file match original series title and original title (in place of episode title) of movie description : Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif stn_y_key in movie_tn_y_dict:

                # Series title of movie file matches title of movie description

                movie_row = movie_rowlist[movie_tn_y_dict[stn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #3 with series title, without episode and with year: Series title of movie file matches title of movie description : Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif stn_y_key in movie_otn_y_dict:

                # Series title of movie file matches original title of movie description

                movie_row = movie_rowlist[movie_otn_y_dict[stn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #4 with series title, without episode and with year: Series title of movie file matches original title of movie description : Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif tn_y_key in movie_tn_y_dict:

                # Title of movie file matches title of movie description

                movie_row = movie_rowlist[movie_tn_y_dict[tn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #5 with series title, without episode and with year: Title of movie file matches title of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif tn_y_key in movie_otn_y_dict:

                # Title of movie file matches original title of movie description

                movie_row = movie_rowlist[movie_otn_y_dict[tn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #6 with series title, without episode and with year: Title of movie file matches original title of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            else:
                if verbosematching_mode:
                    Msg("Matching info: No match with series title, without episode and with year")

        else:

            # Movie file has no series and episode titles -> only try title

            tn_y_key = title_normalized + "#" + str(year)

            #if verbosematching_mode:
            #    Msg("Matching info: Debug: tn_y_key = "+repr(tn_y_key))

            if tn_y_key in movie_tn_y_dict:

                # Title of movie file matches title of movie description

                movie_row = movie_rowlist[movie_tn_y_dict[tn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #1 with just title and with year: Title of movie file matches title of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            elif tn_y_key in movie_otn_y_dict:

                # Title of movie file matches original title of movie description

                movie_row = movie_rowlist[movie_otn_y_dict[tn_y_key]]
                if verbosematching_mode:
                    Msg("Matching info: Try #2 with just title and with year: Title of movie file matches original title of movie description: Year: "+str(year)+"; Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                if movie_row["idMovie"] != medium_row["idMovie"]:
                    SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)

            else:
                if verbosematching_mode:
                    Msg("Matching info: No match with just title and with year")
    else:

        # Movie file has no year. Try to match without year.

        movie_dn = title

        if series_title_normalized != None and episode_title_normalized != None:

            # Movie file has series and episode titles -> use them first, then try title

            stn_etn_key = series_title_normalized + "#" + episode_title_normalized
            tn_key = title_normalized

            #if verbosematching_mode:
            #    Msg("Matching info: Debug: stn_etn_key = "+repr(stn_etn_key))
            #    Msg("Matching info: Debug: tn_key = "+repr(tn_key))

            if stn_etn_key in movie_stn_etn_dict:

                # Series and episode titles of movie file match series and episode titles of movie description

                i_list = movie_stn_etn_dict[stn_etn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #1 with series/episode and without year: Series and episode titles of movie file match series and episode titles of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by series and episode) more than one movie description: "+repr(medium_row["FilePath"]))

            elif stn_etn_key in movie_ostn_oetn_dict:

                # Series and episode titles of movie file match original series and episode titles of movie description

                i_list = movie_ostn_oetn_dict[stn_etn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #2 with series/episode and without year: Series and episode titles of movie file match original series and episode titles of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by original series and episode) more than one movie description: "+repr(medium_row["FilePath"]))

            elif stn_etn_key in movie_stn_tn_dict:

                # Series and episode titles of movie file match series title and normal title (in place of episode title) of movie description

                i_list = movie_stn_tn_dict[stn_etn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #3 with series/episode and without year: Series and episode titles of movie file match series title and normal title (in place of episode title) of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by series and title as episode) more than one movie description: "+repr(medium_row["FilePath"]))

            elif stn_etn_key in movie_ostn_otn_dict:

                # Series and episode titles of movie file match original series title and original normal title (in place of episode title) of movie description

                i_list = movie_ostn_otn_dict[stn_etn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #4 with series/episode and without year: Series and episode titles of movie file match original series title and original normal title (in place of episode title) of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by original series and title as episode) more than one movie description: "+repr(medium_row["FilePath"]))

            elif tn_key in movie_tn_dict:

                # Title of movie file matches title of movie description

                i_list = movie_tn_dict[tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #5 with series/episode and without year: Title of movie file matches title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by title) more than one movie description: "+repr(medium_row["FilePath"]))

            elif tn_key in movie_otn_dict:

                # Title of movie file matches original title of movie description

                i_list = movie_otn_dict[tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #6 with series/episode and without year: Title of movie file matches original title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by original title) more than one movie description: "+repr(medium_row["FilePath"]))

            else:
                if verbosematching_mode:
                    Msg("Matching info: No match with series/episode and without year")

        elif series_title_normalized != None and episode_title_normalized == None:

            # Movie file has series title but no episode title -> use series title as title, then try title

            stn_tn_key = series_title_normalized + "#" + title_normalized
            stn_key = series_title_normalized
            tn_key = title_normalized

            #if verbosematching_mode:
            #    Msg("Matching info: Debug: stn_tn_key = "+repr(stn_tn_key))
            #    Msg("Matching info: Debug: stn_key = "+repr(stn_key))
            #    Msg("Matching info: Debug: tn_key = "+repr(tn_key))

            if stn_tn_key in movie_stn_tn_dict:

                # Series title and normal title of movie file match series title and normal title of movie description

                i_list = movie_stn_tn_dict[stn_tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #1 with series title, without episode and without year: Series title and normal title of movie file match series title and normal title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by series and title) more than one movie description: "+repr(medium_row["FilePath"]))

            elif stn_tn_key in movie_ostn_otn_dict:

                # Original series title and original title of movie file match original series title and original title of movie description

                i_list = movie_ostn_otn_dict[stn_tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #2 with series title, without episode and without year: Original series title and original title of movie file match original series title and original title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by original series and title) more than one movie description: "+repr(medium_row["FilePath"]))

            elif stn_key in movie_tn_dict:

                # Series title of movie file matches title of movie description

                i_list = movie_tn_dict[stn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #3 with series title, without episode and without year: Series title of movie file matches title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by series vs. title) more than one movie description: "+repr(medium_row["FilePath"]))

            elif stn_key in movie_otn_dict:

                # Series title of movie file matches title of movie description

                i_list = movie_otn_dict[stn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #4 with series title, without episode and without year: Series title of movie file matches original title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by original series vs. title) more than one movie description: "+repr(medium_row["FilePath"]))

            elif tn_key in movie_tn_dict:

                # Title of movie file matches title of movie description

                i_list = movie_tn_dict[tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #5 with series title, without episode and without year: Title of movie file matches title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by title) more than one movie description: "+repr(medium_row["FilePath"]))

            elif tn_key in movie_otn_dict:

                # Title of movie file matches original title of movie description

                i_list = movie_otn_dict[tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #6 with series title, without episode and without year: Title of movie file matches original title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by original title) more than one movie description: "+repr(medium_row["FilePath"]))

            else:
                if verbosematching_mode:
                    Msg("Matching info: No match with series title, without episode and with year")

        else:

            # Movie file has no series and episode titles -> only try title

            tn_key = title_normalized

            #if verbosematching_mode:
            #    Msg("Matching info: Debug: tn_key = "+repr(tn_key))

            if tn_key in movie_tn_dict:

                # Title of movie file matches title of movie description

                i_list = movie_tn_dict[tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #1 with just title and without year: Title of movie file matches title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by title) more than one movie description: "+repr(medium_row["FilePath"]))

            elif tn_key in movie_otn_dict:

                # Title of movie file matches original title of movie description

                i_list = movie_otn_dict[tn_key]
                if len(i_list) == 1:
                    movie_row = movie_rowlist[i_list[0]]
                    if verbosematching_mode:
                        Msg("Matching info: Try #2 with just title and without year: Title of movie file matches original title of movie description: Title: "+repr(movie_row["Title"])+"; Original Title: "+repr(movie_row["OriginalTitle"])+"; Episode Title: "+repr(movie_row["EpisodeTitle"])+"; Original Episode Title: "+repr(movie_row["OriginalEpisodeTitle"]))
                    if movie_row["idMovie"] != medium_row["idMovie"]:
                        SetIdMovieInMedium(movie_row["idMovie"], medium_row["idMedium"], movie_dn)
                else:
                    # more than one matching movie
                    ErrorMsg("Skipping movie file without release year that matches (by original title) more than one movie description: "+repr(medium_row["FilePath"]))

            else:
                if verbosematching_mode:
                    Msg("Matching info: No match with just title and without year")


if num_errors > 0:
    ErrorMsg("Finished with "+str(num_errors)+" errors.")
    exit(12)
else:
    exit(0)

