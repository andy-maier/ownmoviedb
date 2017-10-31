#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf-8
#
# Checks the movie database for consistency and displays messages for any inconsistencies detected.
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

my_version = "1.0.1"

import re, sys, glob, os, os.path, string, errno, locale, fnmatch, subprocess, xml.etree.ElementTree, datetime
from operator import itemgetter, attrgetter, methodcaller
import MySQLdb
import movies_conf

my_name = os.path.basename(os.path.splitext(sys.argv[0])[0])

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
    print "Checks the movie database for consistency and displays messages for any inconsistencies detected."
    print "Checks performed: TBD"
    print ""
    print "Usage:"
    print "  "+my_name+" [options]"
    print ""
    print "Options:"
    print "  -v          Verbose mode: Display additional messages."
    print "  -h, --help  Display this help text."
    print ""
    print "Movie database:"
    print "  MySQL host: "+movies_conf.mysql_host+" (default port 3306)"
    print "  MySQL user: "+movies_conf.mysql_user+" (no password)"
    print "  MySQL database: "+movies_conf.mysql_db
    print ""

    return


#------------------------------------------------------------------------------
def ErrorMsg(msg):
    """Prints an error message to stdout.

    Parameters:
        msg:        Message string (str or unicode type).
                    The string "Error: " gets added to the message string.

    Returns nothing
    """

    global num_errors

    msg = "Error: "+msg

    if type(msg) == unicode:
        msgu = msg
    else:
        msgu = msg.decode()
    encoding = sys.stdout.encoding if sys.stdout.encoding else sys.getfilesystemencoding()
    msg = msgu.encode(encoding, "backslashreplace")

    print >>sys.stdout, msg
    sys.stdout.flush()

    num_errors += 1

    return


#------------------------------------------------------------------------------
def WarningMsg(msg):
    """Prints a warning message to stdout.

    Parameters:
        msg:        Message string (str or unicode type).
                    The string "Warning: " gets added to the message string.

    Returns nothing
    """

    msg = "Warning: "+msg

    if type(msg) == unicode:
        msgu = msg
    else:
        msgu = msg.decode()
    encoding = sys.stdout.encoding if sys.stdout.encoding else sys.getfilesystemencoding()
    msg = msgu.encode(encoding, "backslashreplace")

    print >>sys.stdout, msg
    sys.stdout.flush()

    return


#------------------------------------------------------------------------------
def Msg(msg):
    """Prints a message to stdout if in verbose mode.

    Parameters:
        msg:        Message string (str or unicode type).

    Returns nothing
    """

    global verbose_mode

    if verbose_mode:

        if type(msg) == unicode:
            msgu = msg
        else:
            msgu = msg.decode()
        encoding = sys.stdout.encoding if sys.stdout.encoding else sys.getfilesystemencoding()
        msg = msgu.encode(encoding, "backslashreplace")

        print >>sys.stdout, msg
        sys.stdout.flush()

    return


#------------------------------------------------------------------------------

# Translation table for normalizing the movie title
normalize_utrans_table = [
    (228, 'ae'),  # a umlaut
    (246, 'oe'),  # o umlaut
    (252, 'ue'),  # u umlaut
    (223, 'ss'),  # german sharp s
    (196, 'Ae'),  # A umlaut
    (214, 'Oe'),  # O umlaut
    (220, 'Ue'),  # U umlaut
    (225, 'a'),   # a aigue
    (224, 'a'),   # a grave
    (226, 'a'),   # a circumflex
    (233, 'e'),   # e aigue
    (232, 'e'),   # e grave
    (234, 'e'),   # e circumflex
    (237, 'i'),   # i aigue
    (236, 'i'),   # i grave
    (238, 'i'),   # i circumflex
    (243, 'o'),   # o aigue
    (242, 'o'),   # o grave
    (244, 'o'),   # o circumflex
    (250, 'u'),   # u aigue
    (249, 'u'),   # u grave
    (251, 'u'),   # u circumflex
    (193, 'A'),   # A aigue
    (192, 'A'),   # A grave
    (194, 'A'),   # A circumflex
    (201, 'E'),   # E aigue
    (200, 'E'),   # E grave
    (202, 'E'),   # E circumflex
    (205, 'I'),   # I aigue
    (204, 'I'),   # I grave
    (206, 'I'),   # I circumflex
    (211, 'O'),   # O aigue
    (210, 'O'),   # O grave
    (212, 'O'),   # O circumflex
    (218, 'U'),   # U aigue
    (217, 'U'),   # U grave
    (219, 'U'),   # U circumflex
    (219, 'U'),   # U circumflex
    (40,  ''),    # (
    (41,  ''),    # )
    (95,  ''),    # _
    (45,  ''),    # -
    (44,  ''),    # ,
    (33,  ''),    # !
    (38,  ''),    # &
    (59,  ''),    # ;
    (43,  ''),    # +
    (42,  ''),    # *
    (35,  ''),    # #
    (39,  ''),    # '
    (61,  ''),    # =
    (37,  ''),    # %
    (36,  ''),    # $
    (46,  ''),    # .
    (91,  ''),    # [
    (93,  ''),    # ]
    (64,  ''),    # @
]

#------------------------------------------------------------------------------
def NormalizeTitle(title):
    # title is a unicode string

    global normalize_utrans_table

    ntitle = title
    for fm_ord,to_str in normalize_utrans_table:
        ntitle = ntitle.replace(unichr(fm_ord),to_str)
    ntitle = ntitle.lower()
    ntitle = ntitle.replace("  "," ")
    ntitle = ntitle.replace("  "," ")
    ntitle = ntitle.replace("  "," ")
    ntitle = ntitle.strip(" ")

    return ntitle


#------------------------------------------------------------------------------
def GetMovieRow(mymdbimport_row, movie_dn):

    # Columns in Movie table:       Columns in MyMDbImport table:
    #
    #                               Nr.
    #                               Cover
    # idMovie
    # Title                         Titel
    # TitleNormalized               TitleNormalized (was added to rowlist)
    # OriginalTitle                 org. Titel
    # SeriesTitle
    # OriginalSeriesTitle
    # EpisodeTitle
    # OriginalEpisodeTitle
    # SeasonNumber
    # EpisodeNumber
    # RunningNumber
    # CoverImage
    # Duration                      Laenge (mit a umlaut)
    # Description                   Plot
    # ReleaseYear                   Jahr
    # ReleaseCountry                Land (different values)
    # AspectRatio                   Bildformat (different values)
    # Language                      Sprache (different values)
    # OriginalLanguage
    # HasSubtitles
    # SubtitleLanguage
    # IsColored                     Farbe (different values)
    # IsSilent
    # FSK                           FSK
    # IMDbLink                      IMDb
    # IMDbRating                    IMDb Note
    # IMDbRaters                    IMDb Votes
    # OFDbLink                      OFDb
    # OFDbRating                    OFDb Note
    # OFDbRaters                    OFDb Votes
    #
    # to MovieGenre table           Genre
    # to MoviePerson table          Regie
    # to MoviePerson table          Schauspieler

    movie_row = dict()

    movie_row["Title"] = mymdbimport_row["Titel"]
    movie_row["TitleNormalized"] = mymdbimport_row["TitleNormalized"]
    movie_row["OriginalTitle"] = mymdbimport_row["org. Titel"]
    #movie_row["SeriesTitle"] = None
    #movie_row["OriginalSeriesTitle"] = None
    #movie_row["EpisodeTitle"] = None
    #movie_row["OriginalEpisodeTitle"] = None
    #movie_row["SeasonNumber"] = None
    #movie_row["EpisodeNumber"] = None
    #movie_row["RunningNumber"] = None
    #movie_row["CoverImage"] = None
    col_laenge = "L\xE4nge"
    movie_row["Duration"] = mymdbimport_row[col_laenge]
    movie_row["Description"] = mymdbimport_row["Plot"]
    movie_row["ReleaseYear"] = mymdbimport_row["Jahr"]
    movie_row["OriginatingCountries"] = mymdbimport_row["Land"]
    dar_f, dar_str = GetAspectRatioFromMyMDb(mymdbimport_row["Bildformat"], movie_dn)
    movie_row["AspectRatio"] = dar_f
    movie_row["AspectRatioStr"] = dar_str
    movie_row["Language"] = GetLanguageCode(mymdbimport_row["Sprache"], movie_dn)
    #movie_row["OriginalLanguage"] = None
    #movie_row["HasSubtitles"] = None
    #movie_row["SubtitleLanguage"] None
    movie_row["IsColored"] = (mymdbimport_row["Farbe"]  == "Farbe")
    #movie_row["IsSilent"] = None
    movie_row["FSK"] = mymdbimport_row["FSK"]
    movie_row["IMDbLink"] = mymdbimport_row["IMDb"]
    movie_row["IMDbRating"] = mymdbimport_row["IMDb Note"]
    movie_row["IMDbRaters"] = mymdbimport_row["IMDb Votes"]
    movie_row["OFDbLink"] = mymdbimport_row["OFDb"]
    movie_row["OFDbRating"] = mymdbimport_row["OFDb Note"]
    movie_row["OFDbRaters"] = mymdbimport_row["OFDb Votes"]

    return movie_row


#------------------------------------------------------------------------------
def UpdateMovie(mymdbimport_row, movie_row):

    max_dar_failure    = 0.02      # allowable relative difference when comparing aspect ratios expressed as float numbers
    max_rating_failure = 0.001     # allowable relative difference when comparing ratings expressed as float numbers

    idMovie = movie_row["idMovie"]

    year =  movie_row["ReleaseYear"]
    title = movie_row["Title"]
    movie_dn = title +" ("+str(year)+")"

    # Msg("Debug: mymdbimport_row = "+str(mymdbimport_row))

    new_movie_row = GetMovieRow(mymdbimport_row, movie_dn)

    # Msg("Debug: movie_row = "+str(movie_row))

    # Msg("Debug: new_movie_row = "+str(new_movie_row))

    if new_movie_row["TitleNormalized"     ] != movie_row["TitleNormalized"     ]:
        ErrorMsg("Internal: Normalized title not equal while updating movie entry with id "+str(idMovie)+": existing: '"+movie_row["TitleNormalized"]+"', new: '"+new_movie_row["TitleNormalized"]+"'")

    if new_movie_row["ReleaseYear"         ] != movie_row["ReleaseYear"         ]:
        ErrorMsg("Internal: Release year not equal while updating movie entry with id "+str(idMovie)+": existing: '"+str(movie_row["ReleaseYear"])+"', new: '"+str(new_movie_row["ReleaseYear"])+"'")

    diff_field_list = list()
    if new_movie_row["Title"               ] != movie_row["Title"               ]:
        diff_field_list.append("Title")
    if new_movie_row["OriginalTitle"       ] != movie_row["OriginalTitle"       ]:
        diff_field_list.append("OriginalTitle")
    if new_movie_row["Duration"            ] != movie_row["Duration"            ]:
        diff_field_list.append("Duration")
    if new_movie_row["Description"         ] != movie_row["Description"         ]:
        diff_field_list.append("Description")
    if new_movie_row["OriginatingCountries"] != movie_row["OriginatingCountries"]:
        diff_field_list.append("OriginatingCountries")
    if not isEqualFloat(new_movie_row["AspectRatio"], movie_row["AspectRatio"], max_dar_failure):
        diff_field_list.append("AspectRatio")
    if new_movie_row["AspectRatioStr"      ] != movie_row["AspectRatioStr"      ]:
        diff_field_list.append("AspectRatioStr")
    if new_movie_row["Language"            ] != movie_row["Language"            ]:
        diff_field_list.append("Language")
    if new_movie_row["IsColored"           ] != movie_row["IsColored"           ]:
        diff_field_list.append("IsColored")
    if new_movie_row["FSK"                 ] != movie_row["FSK"                 ]:
        diff_field_list.append("FSK")
    if new_movie_row["IMDbLink"            ] != movie_row["IMDbLink"            ]:
        diff_field_list.append("IMDbLink")
    if not isEqualFloat(new_movie_row["IMDbRating"], movie_row["IMDbRating"], max_rating_failure):
        diff_field_list.append("IMDbRating")
    if new_movie_row["IMDbRaters"          ] != movie_row["IMDbRaters"          ]:
        diff_field_list.append("IMDbRaters")
    if new_movie_row["OFDbLink"            ] != movie_row["OFDbLink"            ]:
        diff_field_list.append("OFDbLink")
    if not isEqualFloat(new_movie_row["OFDbRating"], movie_row["OFDbRating"], max_rating_failure):
        diff_field_list.append("OFDbRating")
    if new_movie_row["OFDbRaters"          ] != movie_row["OFDbRaters"          ]:
        diff_field_list.append("OFDbRaters")

    # new_movie_row["SeriesTitle"         ] != movie_row["SeriesTitle"         ]
    # new_movie_row["OriginalSeriesTitle" ] != movie_row["OriginalSeriesTitle" ]
    # new_movie_row["EpisodeTitle"        ] != movie_row["EpisodeTitle"        ]
    # new_movie_row["OriginalEpisodeTitle"] != movie_row["OriginalEpisodeTitle"]
    # new_movie_row["SeasonNumber"        ] != movie_row["SeasonNumber"        ]
    # new_movie_row["EpisodeNumber"       ] != movie_row["EpisodeNumber"       ]
    # new_movie_row["RunningNumber"       ] != movie_row["RunningNumber"       ]
    # new_movie_row["CoverImage"          ] != movie_row["CoverImage"          ]
    # new_movie_row["OriginalLanguage"    ] != movie_row["OriginalLanguage"    ]
    # new_movie_row["HasSubtitles"        ] != movie_row["HasSubtitles"        ]
    # new_movie_row["SubtitleLanguage"    ] != movie_row["SubtitleLanguage"    ]
    # new_movie_row["IsSilent"            ] != movie_row["IsSilent"            ]

    if len(diff_field_list) > 0:

        Msg("Updating movie: "+movie_dn)

        for diff_field in diff_field_list:
            Msg("Difference in field "+diff_field+": existing: '"+str(movie_row[diff_field])+"', new: '"+str(new_movie_row[diff_field])+"'")


        cv = ""          # column=value list for UPDATE
        cv += "Title = %(Title)s, "
        cv += "TitleNormalized = %(TitleNormalized)s, "
        cv += "OriginalTitle = %(OriginalTitle)s, "
        #cv += "SeriesTitle = %(SeriesTitle)s, "
        #cv += "OriginalSeriesTitle = %(OriginalSeriesTitle)s, "
        #cv += "EpisodeTitle = %(EpisodeTitle)s, "
        #cv += "OriginalEpisodeTitle = %(OriginalEpisodeTitle)s, "
        #cv += "SeasonNumber = %(SeasonNumber)s, "
        #cv += "EpisodeNumber = %(EpisodeNumber)s, "
        #cv += "RunningNumber = %(RunningNumber)s, "
        #cv += "CoverImage = %(CoverImage)s, "
        cv += "Duration = %(Duration)s, "
        cv += "Description = %(Description)s, "
        cv += "ReleaseYear = %(ReleaseYear)s, "
        cv += "OriginatingCountries = %(OriginatingCountries)s, "
        cv += "AspectRatio = %(AspectRatio)s, "
        cv += "AspectRatioStr = %(AspectRatioStr)s, "
        cv += "Language = %(Language)s, "
        #cv += "OriginalLanguage = %(OriginalLanguage)s, "
        #cv += "HasSubtitles = %(HasSubtitles)s, "
        #cv += "SubtitleLanguage = %(SubtitleLanguage)s, "
        cv += "IsColored = %(IsColored)s, "
        #cv += "IsSilent = %(IsSilent)s, "
        cv += "FSK = %(FSK)s, "
        cv += "IMDbLink = %(IMDbLink)s, "
        cv += "IMDbRating = %(IMDbRating)s, "
        cv += "IMDbRaters = %(IMDbRaters)s, "
        cv += "OFDbLink = %(OFDbLink)s, "
        cv += "OFDbRating = %(OFDbRating)s, "
        cv += "OFDbRaters = %(OFDbRaters)s"

        sql = "UPDATE Movie SET "+cv+" WHERE idMovie = '"+str(idMovie)+"'"
        # Msg("Debug: sql = "+sql)

        medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)

        medium_cursor.execute(sql,new_movie_row)

        medium_cursor.close()

        movies_conn.commit()

    else:
        pass

        # Msg("Debug: No need to update movie: "+movie_dn)


#------------------------------------------------------------------------------
def AddMovie(mymdbimport_row):

    new_title = mymdbimport_row["Titel"]
    new_year =  mymdbimport_row["Jahr"]
    movie_dn = new_title+" ("+str(new_year)+")"

    Msg("Adding movie: "+movie_dn)

    # Msg("Debug: mymdbimport_row = "+str(mymdbimport_row))

    new_movie_row = GetMovieRow(mymdbimport_row, movie_dn)

    # Msg("Debug: new_movie_row = "+str(new_movie_row))

    c = ""          # column list for INSERT
    v = ""          # value list for INSERT
    c += "Title, "
    v += "%(Title)s, "
    c += "TitleNormalized, "
    v += "%(TitleNormalized)s, "
    c += "OriginalTitle, "
    v += "%(OriginalTitle)s, "
    #c += "SeriesTitle, "
    #v += "%(SeriesTitle)s, "
    #c += "OriginalSeriesTitle, "
    #v += "%(OriginalSeriesTitle)s, "
    #c += "EpisodeTitle, "
    #v += "%(EpisodeTitle)s, "
    #c += "OriginalEpisodeTitle, "
    #v += "%(OriginalEpisodeTitle)s, "
    #c += "SeasonNumber, "
    #v += "%(SeasonNumber)s, "
    #c += "EpisodeNumber, "
    #v += "%(EpisodeNumber)s, "
    #c += "RunningNumber, "
    #v += "%(RunningNumber)s, "
    #c += "CoverImage, "
    #v += "%(CoverImage)s, "
    c += "Duration, "
    v += "%(Duration)s, "
    c += "Description, "
    v += "%(Description)s, "
    c += "ReleaseYear, "
    v += "%(ReleaseYear)s, "
    c += "OriginatingCountries, "
    v += "%(OriginatingCountries)s, "
    c += "AspectRatio, "
    v += "%(AspectRatio)s, "
    c += "AspectRatioStr, "
    v += "%(AspectRatioStr)s, "
    c += "Language, "
    v += "%(Language)s, "
    #c += "OriginalLanguage, "
    #v += "%(OriginalLanguage)s, "
    #c += "HasSubtitles, "
    #v += "%(HasSubtitles)s, "
    #c += "SubtitleLanguage, "
    #v += "%(SubtitleLanguage)s, "
    c += "IsColored, "
    v += "%(IsColored)s, "
    #c += "IsSilent, "
    #v += "%(IsSilent)s, "
    c += "FSK, "
    v += "%(FSK)s, "
    c += "IMDbLink, "
    v += "%(IMDbLink)s, "
    c += "IMDbRating, "
    v += "%(IMDbRating)s, "
    c += "IMDbRaters, "
    v += "%(IMDbRaters)s, "
    c += "OFDbLink, "
    v += "%(OFDbLink)s, "
    c += "OFDbRating, "
    v += "%(OFDbRating)s, "
    c += "OFDbRaters"
    v += "%(OFDbRaters)s"

    sql = "INSERT INTO Movie ("+c+") VALUES ( "+v+")"
    # Msg("Debug: sql = "+sql)

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)

    medium_cursor.execute(sql,new_movie_row)

    medium_cursor.close()

    movies_conn.commit()


#------------------------------------------------------------------------------
def SetIdMovieInMedium(new_idMovie, idMedium, movie_dn):

    Msg("Linking movie file to movie: "+movie_dn)

    sql = "UPDATE Medium SET idMovie = '"+str(new_idMovie)+"' WHERE idMedium = '"+str(idMedium)+"'"
    # Msg("Debug: sql = "+sql)

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)

    medium_cursor.execute(sql)

    medium_cursor.close()

    movies_conn.commit()


#------------------------------------------------------------------------------
countrycode_de_dict = dict( {   # dictionary of country codes (subset)
                                # key: country name in German (unicode string)
                                # value: country code
    u"afghanistan": "af",
    u"albanien": "al",
    u"algerien": "dz",
    u"argentinien": "ar",
    u"australien": "au",
    u"belgien": "be",
    u"bolivien": "bo",
    u"bosnien und herzegowina": "ba",
    u"bosnien": "ba",
    u"brasilien": "br",
    u"bulgarien": "bg",
    u"chile": "cl",
    u"china": "cn",
    u"ddr": "ddde",
    u"deutschland": "de",
    u"d\u00E4nemark": "dk",
    u"england": "uk",
    u"estland": "ee",
    u"finnland": "fi",
    u"frankreich": "fr",
    u"georgien": "ge",
    u"griechenland": "gr",
    u"gro\u00DFbritannien": "uk",
    u"gr\u00F6nland": "gl",
    u"haiti": "ht",
    u"holland": "nl",
    u"hongkong": "hk",
    u"indien": "in",
    u"indonesien": "id",
    u"iran": "ir",
    u"irland": "ie",
    u"islamische republik iran": "ir",
    u"island": "is",
    u"israel": "il",
    u"italien": "it",
    u"jamaika": "jm",
    u"japan": "jp",
    u"jugoslawien": "yu",
    u"kambodscha": "kh",
    u"kanada": "ca",
    u"kasachstan": "kz",
    u"kenia": "ke",
    u"kolumbien": "co",
    u"kroatien": "hr",
    u"kuba": "cu",
    u"lettland": "lv",
    u"libanon": "lb",
    u"liberia": "lr",
    u"libyen": "ly",
    u"libysch-arabische dschamahirija": "ly",
    u"liechtenstein": "li",
    u"litauen": "lt",
    u"luxemburg": "lu",
    u"malta": "mt",
    u"mexiko": "mx",
    u"moldawien": "md",
    u"mongolei": "mn",
    u"namibia": "na",
    u"nepal": "np",
    u"neuseeland": "nz",
    u"niederlande": "nl",
    u"norwegen": "no",
    u"pakistan": "pk",
    u"panama": "pa",
    u"peru": "pe",
    u"philippinen": "ph",
    u"polen": "pl",
    u"portugal": "pt",
    u"republik korea": "rk",
    u"republik moldau": "md",
    u"rum\u00E4nien": "ro",
    u"russische f\u00F6deration": "ru",
    u"russland": "ru",
    u"schweden": "se",
    u"schweiz": "ch",
    u"serbien": "rs",
    u"slowakei": "sk",
    u"slowenien": "si",
    u"sowjetunion": "su",
    u"spanien": "es",
    u"s\u00FCdafrika": "za",
    u"s\u00FCdkorea": "rk",
    u"taiwan": "tw",
    u"thailand": "th",
    u"tschechische republik": "cz",
    u"tschechoslowakei": "cs",
    u"tunesien": "tn",
    u"t\u00FCrkei": "tr",
    u"usa": "us",
    u"udssr": "su",
    u"ukraine": "ua",
    u"ungarn": "hu",
    u"uruguay": "uy",
    u"usbekistan": "uz",
    u"vatikanstadt": "va",
    u"venezuela": "ve",
    u"vereinigte staaten von amerika": "us",
    u"vereinigte staaten": "us",
    u"vereinigtes k\u00F6nigreich": "uk",
    u"vietnam": "vn",
    u"volksrepublik china": "cn",
    u"zypern": "cy",
    u"\u00E4gypten": "eg",
    u"\u00F6sterreich": "at",
    u"#n/a": None,
})


#------------------------------------------------------------------------------
def GetCountryCode(land,movie_dn):
    # land: comma separated list of country names in mixed case in german (unicode string)

    global countrycode_de_dict

    land_l = land.lower()

    # TBD: Multiple countries as comma separated list not supported

    if land_l in countrycode_de_dict:
        cc = countrycode_de_dict[land_l]
    else:
        ErrorMsg("Did not find country code for country '"+land+"' for movie: "+movie_dn)
        cc = None

    return cc


#------------------------------------------------------------------------------
def GetAspectRatioFromMyMDb(bildformat,movie_dn):
    # bildformat: aspect ratio, in various formats:
    #             16:9
    #             16x9
    #             1.778
    #             1.778:1
    #             1.778:1 (some text) - any format can be followed by text in parenthesis
    # return: tuple:
    #  dar_f: aspect ratio as a float number, e.g. 1.778
    #  dar_s: aspect ratio as a display string, e.g. "16x9"

    result_delimiter = "x"    # delimiter between width and height to be used in result
    max_dar_failure = 0.02        # max failure for recognizing whole ratios

    # strip off text in parenthesis

    bf_pp = bildformat.find("(")
    if bf_pp >= 0:
        bf = bildformat[0:bf_pp].strip(" ")
    else:
        bf = bildformat.strip(" ")

    # Msg("Debug: bf = '"+bf+"'")

    # process the format of the remaining text

    if re.match("^[0-9]+x[0-9]+$", bf):
        nom,den = bf.split("x")
        dar_f = float(nom) / float(den)
        dar_s = bf.replace("x",result_delimiter)
    elif re.match("^[0-9]+\:[0-9]+$", bf):
        nom,den = bf.split(":")
        dar_f = float(nom) / float(den)
        dar_s = bf.replace(":",result_delimiter)
    elif re.match("^[0-9]+\.[0-9]+$", bf):
        dar_f = float(bf)
        if isEqualFloat(dar_f, float(4)/float(3), max_dar_failure):
            dar_s = "4"+result_delimiter+"3"
        elif isEqualFloat(dar_f, float(5)/float(4), max_dar_failure):
            dar_s = "5"+result_delimiter+"4"
        elif isEqualFloat(dar_f, float(16)/float(9), max_dar_failure):
            dar_s = "16"+result_delimiter+"9"
        else:
            ErrorMsg("Unknown format '"+bildformat+"' for 'bildformat' column (1 dar_f="+str(dar_f)+") of MyMDb import data for movie: "+movie_dn)
            dar_s = str(dar_f)
    elif re.match("^[0-9]+\.[0-9]+\:[0-9]+$", bf):
        nom,den = bf.split(":")
        dar_f = float(nom) / float(den)
        if isEqualFloat(dar_f, float(4)/float(3), max_dar_failure):
            dar_s = "4"+result_delimiter+"3"
        elif isEqualFloat(dar_f, float(5)/float(4), max_dar_failure):
            dar_s = "5"+result_delimiter+"4"
        elif isEqualFloat(dar_f, float(16)/float(9), max_dar_failure):
            dar_s = "16"+result_delimiter+"9"
        else:
            ErrorMsg("Unknown format '"+bildformat+"' for 'bildformat' column (2 dar_f="+str(dar_f)+") of MyMDb import data for movie: "+movie_dn)
            dar_s = str(dar_f)
    else:
        ErrorMsg("Unknown format '"+bildformat+"' for 'bildformat' column of MyMDb import data for movie: "+movie_dn)
        dar_s = bf
        dar_f = None

    # Msg("Debug: dar_s = '"+dar_s+"', dar_f = "+dar_f)

    return dar_f, dar_s

#------------------------------------------------------------------------------
languagecode_de_dict = dict({   # dictionary of language codes (subset)
                                # key: language name in German (unicode string)
                                # value: language code
    u"deutsch": "de",
    u"arabisch": "ar",
    u"englisch": "en",
    u"franz\u00F6sisch": "fr",
    u"spanisch": "es",
    u"#n/a": None,
})


#------------------------------------------------------------------------------
def isEqualFloat(float1, float2, max_failure):
    # Returns whether float1 and float2 are equal, with a permissible maximum relative failure (max_failure).
    # float1 and float2 may also be None or 0.

    if float1 == None and float2 == None:
        eq = True

    elif float1 == None and float2 != None:
        eq = False

    elif float1 != None and float2 == None:
        eq = False

    elif float1 == 0 and float2 == 0:
        eq = True

    elif float1 == 0 and float2 != 0:
        eq = False

    elif float1 != 0 and float2 == 0:
        eq = False

    else:
        ffloat1 = float(float1)
        ffloat2 = float(float2)

        failure = ffloat1 / ffloat2 - 1

        # Msg("Debug: ffloat1="+str(ffloat1)+" ffloat2="+str(ffloat2)+" failure="+str(failure))

        if abs(failure) <= max_failure:
            eq = True
        else:
            eq = False

    return eq


#------------------------------------------------------------------------------
def GetLanguageCode(sprache,movie_dn):

    global languagecode_de_dict

    # Msg("Debug: type sprache = "+str(type(sprache)))
    # Msg("Debug: sprache = '"+str(sprache)+"'")

    sprache_l = sprache.lower()

    if sprache_l in languagecode_de_dict:
        lc = languagecode_de_dict[sprache_l]
    else:
        ErrorMsg("Did not find language code for language '"+sprache+"' for movie: "+movie_dn)
        lc = None

    return lc


#------------------------------------------------------------------------------
def GetIdVideoQuality(name, file):

    global idvideoquality_dict

    if name in idvideoquality_dict:
        id = idvideoquality_dict[name]
    else:
        id = None
        ErrorMsg("Video quality name '"+name+"' not found in movie database, file: "+file)

    return id

#------------------------------------------------------------------------------
def GetIdContainerFormat(field_value, file):

    global idcontainerformat_dict

    if field_value in idcontainerformat_dict:
        id = idcontainerformat_dict[field_value]
    else:
        id = None
        ErrorMsg("Container format field value '"+field_value+"' not found in movie database, file: "+file)

    return id

#------------------------------------------------------------------------------
def GetIdVideoFormat(format_field_value, profile_field_value, file):

    global fixedvideoformat_list

    id = None
    for _row in fixedvideoformat_list:
        if _row["FormatFieldValue"] == format_field_value:
            if _row["ProfileFieldValue"] == profile_field_value:
                id = _row["idVideoFormat"]
                break
            elif _row["ProfileFieldValue"] == None:
                id = _row["idVideoFormat"]
                break

    if id == None:
        ErrorMsg("Video format field value '"+format_field_value+"' and profile field value '"+str(profile_field_value)+"' not found in movie database, file: "+file)

    return id

#------------------------------------------------------------------------------
def GetIdAudioFormat(format_field_value, profile_field_value, file):

    global fixedaudioformat_list

    id = None
    for _row in fixedaudioformat_list:
        if _row["FormatFieldValue"] == format_field_value:
            if _row["ProfileFieldValue"] == profile_field_value:
                id = _row["idAudioFormat"]
                break
            elif _row["ProfileFieldValue"] == None:
                id = _row["idAudioFormat"]
                break

    if id == None:
        ErrorMsg("Audio format field value '"+format_field_value+"' and profile field value '"+str(profile_field_value)+"' not found in movie database, file: "+file)

    return id

#------------------------------------------------------------------------------
def GetIdVideoFramerateMode(field_value, file):

    global idvideoframeratemode_dict

    if field_value in idvideoframeratemode_dict:
        id = idvideoframeratemode_dict[field_value]
    else:
        id = None
        ErrorMsg("Video framerate mode field value '"+field_value+"' not found in movie database, file: "+file)

    return id

#------------------------------------------------------------------------------
def GetIdAudioBitrateMode(field_value, file):

    global idaudiobitratemode_dict

    if field_value in idaudiobitratemode_dict:
        id = idaudiobitratemode_dict[field_value]
    else:
        id = None
        ErrorMsg("Audio bitrate mode field value '"+field_value+"' not found in movie database, file: "+file)

    return id

#------------------------------------------------------------------------------
def GetIdCabinet(smb_server_resource, file):

    global idcabinet_dict

    if smb_server_resource in idcabinet_dict:
        id = idcabinet_dict[smb_server_resource]
    else:
        id = None
        ErrorMsg("Media cabinet for SMB server resource '"+smb_server_resource+"' not found in movie database, file: "+file)

    return id


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
        if arg == "-h" or arg == "--help":
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
movies_conn = MySQLdb.connect( host=movies_conf.mysql_host, user=movies_conf.mysql_user,
                               db=movies_conf.mysql_db, use_unicode=True, charset='utf8')


_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute("SELECT * FROM MyMDbImport")
mymdbimport_rowlist = _cursor.fetchall()
_cursor.close()

Msg("Found "+str(len(mymdbimport_rowlist))+" movies in MyMDb import data (MyMDbImport table)")


_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute("SELECT * FROM Movie")
movie_rowlist = _cursor.fetchall()
_cursor.close()

Msg("Found "+str(len(movie_rowlist))+" movies in movie database (Movie table)")

# Msg("Debug: movie_rowlist = "+str(movie_rowlist))


_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute("SELECT * FROM Medium")
medium_rowlist = _cursor.fetchall()
_cursor.close()

Msg("Found "+str(len(medium_rowlist))+" movie files in movie database (Medium table)")


# Add normalized title to the MyMDb import data

for _row in mymdbimport_rowlist:
    title = _row["Titel"]
    ntitle = NormalizeTitle(title)
    _row["TitleNormalized"] = ntitle

# Msg("Debug: mymdbimport_rowlist (with normalized title) = "+str(mymdbimport_rowlist))


# Build dictionary of current Movie table, for fast access

movie_ny_dict = dict()      # dictionary of movies with access by normalized title + year
                            # key: normalized title '#' release year
                            # value: index into movie_rowlist array (0-based)

i = 0
for movie_row in movie_rowlist:
    ntitle = movie_row["TitleNormalized"]
    year = movie_row["ReleaseYear"]
    if year == None:
        ErrorMsg("Movie database inconsistency: Movie with id "+str(movie_row["idMovie"])+" has no release year: '"+movie_row["Title"]+"'")
        # TBD: Update existing movie entry instead of ignoring the existing entry and adding a new one.
    else:
        ny_key = ntitle + "#" + str(year)
        if ny_key in movie_ny_dict:
            existing_movie_row = movie_rowlist[movie_ny_dict[ny_key]]
            existing_movie_dn = existing_movie_row["Title"] + " (" + str(existing_movie_row["ReleaseYear"]) + ")"
            movie_dn = movie_row["Title"] + " (" + str(movie_row["ReleaseYear"]) + ")"
            ErrorMsg("Movie database inconsistency: Movie with id "+str(movie_row["idMovie"])+" is a duplicate of movie with id "+str(existing_movie_row["idMovie"])+": '"+movie_dn+"'")
        else:
            movie_ny_dict[ny_key] = i
    i += 1


# Copy the MyMDb import data into the Movie table, replacing movies that already exist

Msg("Updating movies from MyMDb import data ...")

mymdbimport_ny_dict = dict()      # dictionary of movies in MyMDbImport table, with access by normalized title + year
                                  # key: normalized title '#' release year
                                  # value: index into mymdbimport_rowlist array (0-based)

i = 0
for mymdbimport_row in mymdbimport_rowlist:

    # Try to match the new movie by normalized title and year

    new_ntitle = mymdbimport_row["TitleNormalized"]
    new_year = mymdbimport_row["Jahr"]

    # We need to ensure that the resulting Movie rows have a release year,
    # so we reject any import row that does not have a release year.

    if new_year == None:

        ErrorMsg("Skipping movie in MyMDb import data that does not have a release year: '"+mymdbimport_row["Title"]+"'")

    else:

        ny_key = new_ntitle + "#" + str(new_year)

        # Check if the movie exists in the Movie table
        # TBD: Add other ways to match the movie

        if ny_key in movie_ny_dict:
            # Movie was found in Movie table

            movie_row = movie_rowlist[movie_ny_dict[ny_key]]

            UpdateMovie(mymdbimport_row, movie_row)

        else:
            # Movie was not found in Movie table

            AddMovie(mymdbimport_row)

        # Check for duplicates

        if ny_key in mymdbimport_ny_dict:
            existing_mymdbimport_row = mymdbimport_rowlist[mymdbimport_ny_dict[ny_key]]
            existing_mymdbimport_dn = existing_mymdbimport_row["Titel"] + " (" + str(existing_mymdbimport_row["Jahr"]) + ")"
            mymdbimport_dn = mymdbimport_row["Titel"] + " (" + str(mymdbimport_row["Jahr"]) + ")"
            ErrorMsg("MyMDb import data inconsistency: Movie with nr. "+str(mymdbimport_row["Nr."])+" is a duplicate of movie with nr. "+str(existing_mymdbimport_row["Nr."])+": '"+mymdbimport_dn+"'")
        else:
            mymdbimport_ny_dict[ny_key] = i

    i += 1


# Link the Media table with the updated Movie table (by setting the idMovie column in the Media table)

Msg("Linking movie files to movies in movie database ...")

for medium_row in medium_rowlist:

    ntitle = medium_row["TitleNormalized"]
    year_file = medium_row["ReleaseYearFile"]
    year_tag = medium_row["ReleaseYearTag"]
    if year_file != None:
        year = year_file
    elif year_tag != None:
        year = year_tag
    else:
        year = None

    if year != None:

        ny_key = ntitle + "#" + str(year)

        if ny_key in movie_ny_dict:

            # Matching movie was found

            movie_row = movie_rowlist[movie_ny_dict[ny_key]]

            existing_idMovie = medium_row["idMovie"]
            new_idMovie = movie_row["idMovie"]

            if new_idMovie != existing_idMovie:

                # The new movie id is different than the existing one. Update it.

                idMedium = medium_row["idMedium"]
                movie_dn = movie_row["Title"] + " (" + str(movie_row["ReleaseYear"]) + ")"

                SetIdMovieInMedium(new_idMovie, idMedium, movie_dn)

        else:

            # No matching movie was not found.

            pass # we do not report this, as this happens very often

    else:

        # Movie file has no year. Try to match by just the normalized title.

        found_movie_ix_list = [] # list of indexes into movie_rowlist for matching movies

        ix = 0
        for movie_row in movie_rowlist:
            movie_ntitle = movie_row["TitleNormalized"]
            if movie_ntitle == ntitle:
                found_movie_ix_list.append(ix)
            ix += 1

        num_matching_movies = len(found_movie_ix_list)

        if num_matching_movies > 1:

            ErrorMsg("Found "+str(num_matching_movies)+" movies whose title matches movie file: "+medium_row["FilePath"])

        elif num_matching_movies == 0:

            # No matching movie was not found.

            pass # we do not report this, as this happens very often

        else:

            # Exactly one matching movie was found

            movie_row = movie_rowlist[found_movie_ix_list[0]]

            existing_idMovie = medium_row["idMovie"]
            new_idMovie = movie_row["idMovie"]

            if new_idMovie != existing_idMovie:

                # The new movie id is different than the existing one. Update it.

                idMedium = medium_row["idMedium"]
                movie_dn = movie_row["Title"] + " (" + str(movie_row["ReleaseYear"]) + ")"

                SetIdMovieInMedium(new_idMovie, idMedium, movie_dn)


if num_errors > 0:
    ErrorMsg("Finished with "+str(num_errors)+" errors.")
    exit(12)
else:
    exit(0)

