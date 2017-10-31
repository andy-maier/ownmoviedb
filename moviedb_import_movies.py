#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
# coding: utf-8
#
# Updates movie descriptions in the movie database from a MyMDb export spreadsheet.
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
#   V1.0.3 2012-08-13
#     Initial version with change log.
#   V1.2.0 2012-09-02
#     Renamed package to moviedb and restructured modules.
#   V1.2.2 2012-09-20
#     Added fallback for movie title parsing: If no series/episode information in Kommentar,
#     the title of the movie is parsed for series and episode information.
#   V1.3.0 2012-11-07
#     Improved error message for unknown genre.
#   V1.4.0 2013-09-12
#     Tolerate empty genres (e.g. caused by trailing comma, as in: "Action,").


import re, sys, os.path
import xlrd
import csv, codecs, cStringIO
import MySQLdb
from moviedb import config, utils, version

my_name = os.path.basename(os.path.splitext(sys.argv[0])[0])

layouts = [                     # Layouts of data in spreadsheet
    ("mymdb", u"MyMDb layout: Export of MyMDb view '\u00DCbersicht', with certain fields."),
    ("direct", u"Direct layout: First row in sheet defines column names of Movie table."),
]


#------------------------------------------------------------------------------
def Usage ():
    """Print the command usage to stdout.
       Input:
         n/a
       Return:
         void.
    """

    print ""
    print "Updates movie descriptions in the movie database from a MyMDb export spreadsheet."
    print "By default, only movies that need to be updated based on the new vs. existing data are updated."
    print ""
    print "Usage:"
    print "  "+my_name+" [options]"
    print ""
    print "Required options:"
    print "  -f file     Path name of the MyMDb export spreadsheet file (Excel and CSV only at this point)."
    print "  -s sheet    Name of the sheet within the spreadsheet."
    print "  -l layout   Layout of the data in the sheet. Possible layouts:"
    for _l in layouts:
        _l_name, _l_desc = _l
        print "              "+_l_name+": "+_l_desc
    print ""
    print "Options:"
    print "  -a          Update all movies, instead of just those whose records are outdated."
    print "  -v          Verbose mode: Display additional messages."
    print "  -h, --help  Display this help text."
    print ""
    print "Movie database:"
    print "  MySQL host: "+config.MYSQL_HOST+" (default port 3306)"
    print "  MySQL user: "+config.MYSQL_USER+" (no password)"
    print "  MySQL database: "+config.MYSQL_DB
    print ""
    print "Examples:"
    print "  "+my_name+u" -v -f MyMDb_\u00DCbersicht.xls -s Sheet0 -l mymdb"
    print "  "+my_name+" -v -f Eisenbahnromantik.ods -s Movie-Input -l direct"
    print ""

    return


#------------------------------------------------------------------------------
class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

#------------------------------------------------------------------------------
class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self



#------------------------------------------------------------------------------
def GetDirectorNameLists(ss_row, movie_dn, ss_layout):

    colname = colname_m_l_dict[ss_layout]["Directors"]
    director_ustr = None if colname == None or colname not in ss_row else ss_row[colname]

    if director_ustr == None or director_ustr == "":
        _director_name_list = list()
    else:
        _director_name_list = director_ustr.split(",")

    normalized_director_name_list = []
    director_name_list = []
    directors = ""

    for director_name in _director_name_list:

        director_name = director_name.strip(" ")
        normalized_director_name_list.append(utils.NormalizeString(director_name))
        director_name_list.append(director_name)
        if directors != "":
            directors += ", "
        directors += director_name

    return (normalized_director_name_list,director_name_list,directors)


#------------------------------------------------------------------------------
def GetActorNameLists(ss_row, movie_dn, ss_layout):

    colname = colname_m_l_dict[ss_layout]["Actors"]
    actor_ustr = None if colname == None or colname not in ss_row else ss_row[colname]

    if actor_ustr == None or actor_ustr == "":
        _actor_name_list = list()
    else:
        _actor_name_list = actor_ustr.split(",")

    normalized_actor_name_list = []
    actor_name_list = []
    actors = ""

    for actor_name in _actor_name_list:

        actor_name = actor_name.strip(" ")
        normalized_actor_name_list.append(utils.NormalizeString(actor_name))
        actor_name_list.append(actor_name)
        if actors != "":
            actors += ", "
        actors += actor_name

    return (normalized_actor_name_list,actor_name_list,actors)


#------------------------------------------------------------------------------
def GetGenreIdList(ss_row, movie_dn):

    global genre_nname_dict, genre_rowlist, genre_gid_dict, num_errors

    colname = colname_m_l_dict[ss_layout]["Genres"]
    genre_ustr = None if colname == None or colname not in ss_row else ss_row[colname]

    if genre_ustr == None or genre_ustr == "":
        genre_name_list = list()
    else:
        genre_name_list = genre_ustr.split(",")

    genreid_list = []
    genres = ""

    for genre_name in genre_name_list:

        if genre_name == "":
            continue

        genre_name = genre_name.strip(" ")
        normalized_genre_name = utils.NormalizeString(genre_name)

        if normalized_genre_name in genre_nname_dict:

            genre_row = genre_rowlist[genre_nname_dict[normalized_genre_name]]
            genreid = genre_row["idGenre"]

            org_genreid = OriginalGenreId(genreid,0)
            genreid_list.append(org_genreid)

            org_genre_row = genre_rowlist[genre_gid_dict[org_genreid]]
            if genres != "":
                genres += ", "
            genres += org_genre_row["Name"]

        else:
            utils.ErrorMsg("Genre '"+genre_name+"' not found in Genre table, in movie description for "+movie_dn, num_errors)

    return (genreid_list,genres)


#------------------------------------------------------------------------------
def OriginalGenreId(genreid,nesting):

    global genre_gid_dict, genre_rowlist, num_errors

    genre_row = genre_rowlist[genre_gid_dict[genreid]]

    synof_genreid = genre_row["idSynonymOfGenre"]

    if nesting > 10:
        utils.ErrorMsg("Maximum nesting of "+str(nesting)+" for synonym genres exceeded when reaching genre with id "+str(genreid)+": '"+repr(genre_row["Name"])+"'", num_errors)
        return genreid

    if synof_genreid != None:
        org_genreid = OriginalGenreId(synof_genreid,nesting+1)
    else:
        org_genreid = genreid

    return org_genreid


#------------------------------------------------------------------------------
colname_m_l_dict = {            # Dictionary of column name translations from Movie table to spreadsheet layout
                                # key: name of layout in spreadsheet
                                # value:
                                #   Dictionary of column names
                                #   key: name of column in Movie table
                                #   value: name of column in layout in spreadsheet

    "mymdb": {                  # mymdb layout
        "idMovie":                       None,
        "Title":                         "Titel",
        "OriginalTitle":                 "org. Titel",
        "SeriesTitle":                   "Kommentar",       # entry SeriesTitle:
        "OriginalSeriesTitle":           "Kommentar",       # entry OriginalSeriesTitle:
        "EpisodeTitle":                  "Kommentar",       # entry EpisodeTitle:
        "OriginalEpisodeTitle":          "Kommentar",       # entry OriginalEpisodeTitle:
        "EpisodeId":                     "Kommentar",       # entry EpisodeId:
        "CoverImage":                    None,
        "Duration":                     u"L\u00E4nge",
        "ReleaseYear":                   "Jahr",
        "OriginatingCountries":          "Land",            # different values
        "Genres":                        "Genre",           # Genres go to MovieGenre table
        "Directors":                     "Regie",
        "Actors":                        "Schauspieler",
        "Description":                   "Plot",
        "AspectRatio":                   "Bildformat",      # different values
        "Language":                      "Sprache",         # different values
        "OriginalLanguage":              None,
        "SubtitleLanguage":              None,
        "IsColored":                     "Farbe",           # different values
        "IsSilent":                      None,
        "FSK":                           "FSK",
        "Link":                          None,
        "IMDbLink":                      "IMDb",
        "IMDbRating":                    "IMDb Note",
        "IMDbRaters":                    "IMDb Votes",
        "OFDbLink":                      "OFDb",
        "OFDbRating":                    "OFDb Note",
        "OFDbRaters":                    "OFDb Votes",
    },
    "direct": {
        "idMovie":                       "idMovie",
        "Title":                         "Title",
        "OriginalTitle":                 "OriginalTitle",
        "SeriesTitle":                   "SeriesTitle",
        "OriginalSeriesTitle":           "OriginalSeriesTitle",
        "EpisodeTitle":                  "EpisodeTitle",
        "OriginalEpisodeTitle":          "OriginalEpisodeTitle",
        "EpisodeId":                     "EpisodeId",
        "CoverImage":                    "CoverImage",
        "Duration":                      "Duration",
        "ReleaseYear":                   "ReleaseYear",
        "OriginatingCountries":          "OriginatingCountries",
        "Genres":                        "Genres",
        "Directors":                     "Directors",
        "Actors":                        "Actors",
        "Description":                   "Description",
        "AspectRatio":                   "AspectRatio",
        "Language":                      "Language",
        "OriginalLanguage":              "OriginalLanguage",
        "SubtitleLanguage":              "SubtitleLanguage",
        "IsColored":                     "IsColored",
        "IsSilent":                      "IsSilent",
        "FSK":                           "FSK",
        "Link":                          "Link",
        "IMDbLink":                      "IMDbLink",
        "IMDbRating":                    "IMDbRating",
        "IMDbRaters":                    "IMDbRaters",
        "OFDbLink":                      "OFDbLink",
        "OFDbRating":                    "OFDbRating",
        "OFDbRaters":                    "OFDbRaters",
    }
}

#------------------------------------------------------------------------------
def GetMovieRow(ss_row, movie_dn, ss_layout):

    movie_row = dict()

    colname = colname_m_l_dict[ss_layout]["Title"]
    movie_row["Title"] = None if colname == None or colname not in ss_row else ss_row[colname]

    colname = colname_m_l_dict[ss_layout]["OriginalTitle"]
    movie_row["OriginalTitle"] = None if colname == None or colname not in ss_row else ss_row[colname]

    if ss_layout == "mymdb":


        movie_row["SeriesTitle"] = None
        movie_row["OriginalSeriesTitle"] = None
        movie_row["EpisodeTitle"] = None
        movie_row["OriginalEpisodeTitle"] = None
        movie_row["EpisodeId"] = None

        if movie_row["Title"] != None:

            try:
                parsed_title = utils.ParseComplexTitle(movie_row["Title"])
            except utils.ParseError as exc:
                utils.ErrorMsg(u"Skipping movie: "+unicode(exc))
                raise

            movie_row["SeriesTitle"] = parsed_title["series_title"]
            movie_row["EpisodeTitle"] = parsed_title["episode_title"]
            movie_row["EpisodeId"] = parsed_title["episode_id"]

        if movie_row["OriginalTitle"] != None:

            try:
                parsed_title = utils.ParseComplexTitle(movie_row["OriginalTitle"])
            except utils.ParseError as exc:
                utils.ErrorMsg(u"Skipping movie: "+unicode(exc))
                raise

            movie_row["OriginalSeriesTitle"] = parsed_title["series_title"]
            movie_row["OriginalEpisodeTitle"] =  parsed_title["episode_title"]
            if movie_row["EpisodeId"] == None:
                movie_row["EpisodeId"] = parsed_title["episode_id"]

        kommentar = ss_row["Kommentar"]

        if kommentar != None and kommentar != "":


            k_lines = kommentar.splitlines()

            for k_line in k_lines:

                m = re.match("^SeriesTitle: (.*)$",k_line)
                if m:
                    series_title = m.group(1)
                    movie_row["SeriesTitle"] = series_title.strip(" ")
                    continue # for loop

                m = re.match("^OriginalSeriesTitle: (.*)$",k_line)
                if m:
                    original_series_title = m.group(1)
                    movie_row["OriginalSeriesTitle"] = original_series_title.strip(" ")
                    continue # for loop

                m = re.match("^EpisodeTitle: (.*)$",k_line)
                if m:
                    episode_title = m.group(1)
                    movie_row["EpisodeTitle"] = episode_title.strip(" ")
                    continue # for loop

                m = re.match("^OriginalEpisodeTitle: (.*)$",k_line)
                if m:
                    original_episode_title = m.group(1)
                    movie_row["OriginalEpisodeTitle"] = original_episode_title.strip(" ")
                    continue # for loop

                m = re.match("^EpisodeId: (.*)$",k_line)
                if m:
                    episode_id = m.group(1)
                    movie_row["EpisodeId"] = episode_id.strip(" ")
                    continue # for loop

    else: # direct

        colname = colname_m_l_dict[ss_layout]["SeriesTitle"]
        movie_row["SeriesTitle"] = None if colname == None or colname not in ss_row else ss_row[colname]

        colname = colname_m_l_dict[ss_layout]["OriginalSeriesTitle"]
        movie_row["OriginalSeriesTitle"] = None if colname == None or colname not in ss_row else ss_row[colname]

        colname = colname_m_l_dict[ss_layout]["EpisodeTitle"]
        movie_row["EpisodeTitle"] = None if colname == None or colname not in ss_row else ss_row[colname]

        colname = colname_m_l_dict[ss_layout]["OriginalEpisodeTitle"]
        movie_row["OriginalEpisodeTitle"] = None if colname == None or colname not in ss_row else ss_row[colname]

        colname = colname_m_l_dict[ss_layout]["EpisodeId"]
        movie_row["EpisodeId"] = None if colname == None or colname not in ss_row else ss_row[colname]


    # movie_row["CoverImage"] = None

    colname = colname_m_l_dict[ss_layout]["Duration"]
    if colname == None or colname not in ss_row:
        movie_row["Duration"] = None
    else:
        duration = ss_row[colname] if ss_row[colname] != "" else None
        if duration != None:
            duration = int(float(duration)) # rounds to nearest integer
        movie_row["Duration"] = duration

    colname = colname_m_l_dict[ss_layout]["ReleaseYear"]
    if colname == None or colname not in ss_row:
        movie_row["ReleaseYear"] = None
    else:
        year = ss_row[colname] if ss_row[colname] != "" else None
        if year != None:
            year = int(year)
        movie_row["ReleaseYear"] = year

    colname = colname_m_l_dict[ss_layout]["OriginatingCountries"]
    if colname == None or colname not in ss_row:
        movie_row["OriginatingCountries"] = None
    else:
        movie_row["OriginatingCountries"] = None if ss_row[colname] == "" else ss_row[colname]

    colname = colname_m_l_dict[ss_layout]["Genres"]
    if colname == None or colname not in ss_row:
        movie_row["Genres"] = None
    else:
        movie_row["Genres"] = None if ss_row[colname] == "" else ss_row[colname]

    colname = colname_m_l_dict[ss_layout]["Directors"]
    if colname == None or colname not in ss_row:
        movie_row["Directors"] = None
    else:
        movie_row["Directors"] = None if ss_row[colname] == "" else ss_row[colname]

    colname = colname_m_l_dict[ss_layout]["Actors"]
    if colname == None or colname not in ss_row:
        movie_row["Actors"] = None
    else:
        movie_row["Actors"] = None if ss_row[colname] == "" else ss_row[colname]

    colname = colname_m_l_dict[ss_layout]["Description"]
    if colname == None or colname not in ss_row:
        movie_row["Description"] = None
    else:
        movie_row["Description"] = None if ss_row[colname] == "" else ss_row[colname]

    colname = colname_m_l_dict[ss_layout]["AspectRatio"]
    if colname == None or colname not in ss_row:
        movie_row["AspectRatio"] = None
        movie_row["AspectRatioStr"] = None
    else:
        dar_f, dar_str = GetAspectRatio(ss_row[colname], movie_dn)
        movie_row["AspectRatio"] = dar_f
        movie_row["AspectRatioStr"] = dar_str

    colname = colname_m_l_dict[ss_layout]["Language"]
    if colname == None or colname not in ss_row:
        movie_row["Language"] = None
    else:
        movie_row["Language"] = GetLanguageCode(ss_row[colname], movie_dn)

    #movie_row["OriginalLanguage"] = None

    #movie_row["SubtitleLanguage"] None

    colname = colname_m_l_dict[ss_layout]["IsColored"]
    if colname == None or colname not in ss_row:
        movie_row["IsColored"] = None
    else:
        if ss_layout == "mymdb":
            movie_row["IsColored"] = None if ss_row[colname] == "" else (ss_row[colname] == "Farbe")
        else: # direct
            movie_row["IsColored"] = None if ss_row[colname] == "" else ss_row[colname]

    #movie_row["IsSilent"] = None

    colname = colname_m_l_dict[ss_layout]["FSK"]
    if colname == None or colname not in ss_row:
        movie_row["FSK"] = None
    else:
        fsk = ss_row[colname] if ss_row[colname] != "" else None
        if fsk != None:
            fsk = int(fsk)
        movie_row[colname] = fsk

    colname = colname_m_l_dict[ss_layout]["Link"]
    if colname == None or colname not in ss_row:
        movie_row["Link"] = None
    else:
        movie_row["Link"] = ss_row[colname] if ss_row[colname] != "" else None

    colname = colname_m_l_dict[ss_layout]["IMDbLink"]
    if colname == None or colname not in ss_row:
        movie_row["IMDbLink"] = None
    else:
        movie_row["IMDbLink"] = ss_row[colname] if ss_row[colname] != "" else None

    colname = colname_m_l_dict[ss_layout]["IMDbRating"]
    if colname == None or colname not in ss_row:
        movie_row["IMDbRating"] = None
    else:
        imdb_rating = ss_row[colname] if ss_row[colname] != "" else None
        if imdb_rating != None:
            imdb_rating = float(imdb_rating)
        movie_row["IMDbRating"] = imdb_rating

    colname = colname_m_l_dict[ss_layout]["IMDbRaters"]
    if colname == None or colname not in ss_row:
        movie_row["IMDbRaters"] = None
    else:
        imdb_raters = ss_row[colname] if ss_row[colname] != "" else None
        if imdb_raters != None:
            imdb_raters = int(imdb_raters)
        movie_row["IMDbRaters"] = imdb_raters

    colname = colname_m_l_dict[ss_layout]["OFDbLink"]
    if colname == None or colname not in ss_row:
        movie_row["OFDbLink"] = None
    else:
        movie_row["OFDbLink"] = ss_row[colname] if ss_row[colname] != "" else None

    colname = colname_m_l_dict[ss_layout]["OFDbRating"]
    if colname == None or colname not in ss_row:
        movie_row["OFDbRating"] = None
    else:
        ofdb_rating = ss_row[colname] if ss_row[colname] != "" else None
        if ofdb_rating != None:
            ofdb_rating = float(ofdb_rating)
        movie_row["OFDbRating"] = ofdb_rating

    colname = colname_m_l_dict[ss_layout]["OFDbRaters"]
    if colname == None or colname not in ss_row:
        movie_row["OFDbRaters"] = None
    else:
        ofdb_raters = ss_row[colname] if ss_row[colname] != "" else None
        if ofdb_raters != None:
            ofdb_raters = int(ofdb_raters)
        movie_row["OFDbRaters"] = ofdb_raters

    return movie_row


#------------------------------------------------------------------------------
def UpdateMovie(ss_row, movie_row, ss_layout):

    global movies_conn, genre_rowlist, genre_gid_dict, num_errors, verbose_mode

    max_dar_failure    = 0.02      # allowable relative difference when comparing aspect ratios expressed as float numbers
    max_rating_failure = 0.001     # allowable relative difference when comparing ratings expressed as float numbers

    idMovie = movie_row["idMovie"]

    title = movie_row["Title"]
    year =  int(movie_row["ReleaseYear"])
    movie_dn = title +" ("+str(year)+")"

    new_movie_row = GetMovieRow(ss_row, movie_dn, ss_layout)

    if int(new_movie_row["ReleaseYear"]) != int(movie_row["ReleaseYear"]):
        utils.ErrorMsg("Internal: Release year not equal while updating movie entry with id "+str(idMovie)+": existing: '"+str(int(movie_row["ReleaseYear"]))+"', new: '"+str(int(new_movie_row["ReleaseYear"]))+"'", num_errors)

    diff_field_list = list()
    if new_movie_row["Title"               ] != movie_row["Title"               ]:
        diff_field_list.append("Title")
    if new_movie_row["OriginalTitle"       ] != movie_row["OriginalTitle"       ]:
        diff_field_list.append("OriginalTitle")
    if new_movie_row["SeriesTitle"         ] != movie_row["SeriesTitle"         ]:
        diff_field_list.append("SeriesTitle")
    if new_movie_row["OriginalSeriesTitle" ] != movie_row["OriginalSeriesTitle" ]:
        diff_field_list.append("OriginalSeriesTitle")
    if new_movie_row["EpisodeTitle"        ] != movie_row["EpisodeTitle"        ]:
        diff_field_list.append("EpisodeTitle")
    if new_movie_row["OriginalEpisodeTitle"] != movie_row["OriginalEpisodeTitle"]:
        diff_field_list.append("OriginalEpisodeTitle")
    if new_movie_row["EpisodeId"           ] != movie_row["EpisodeId"           ]:
        diff_field_list.append("EpisodeId")
    if new_movie_row["Duration"            ] != movie_row["Duration"            ]:
        diff_field_list.append("Duration")
    if new_movie_row["OriginatingCountries"] != movie_row["OriginatingCountries"]:
        diff_field_list.append("OriginatingCountries")
    if new_movie_row["Description"         ] != movie_row["Description"         ]:
        diff_field_list.append("Description")
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

    # new_movie_row["CoverImage"          ] != movie_row["CoverImage"          ]
    # new_movie_row["OriginalLanguage"    ] != movie_row["OriginalLanguage"    ]
    # new_movie_row["SubtitleLanguage"    ] != movie_row["SubtitleLanguage"    ]
    # new_movie_row["IsSilent"            ] != movie_row["IsSilent"            ]

    updated_fields = False

    if len(diff_field_list) > 0:

        updated_fields = True

        cv = u""          # column=value list for UPDATE
        cv += "Title = %(Title)s, "
        cv += "OriginalTitle = %(OriginalTitle)s, "
        cv += "SeriesTitle = %(SeriesTitle)s, "
        cv += "OriginalSeriesTitle = %(OriginalSeriesTitle)s, "
        cv += "EpisodeTitle = %(EpisodeTitle)s, "
        cv += "OriginalEpisodeTitle = %(OriginalEpisodeTitle)s, "
        cv += "EpisodeId = %(EpisodeId)s, "
        #cv += "CoverImage = %(CoverImage)s, "
        cv += "Duration = %(Duration)s, "
        cv += "Description = %(Description)s, "
        cv += "ReleaseYear = %(ReleaseYear)s, "
        cv += "OriginatingCountries = %(OriginatingCountries)s, "
        cv += "AspectRatio = %(AspectRatio)s, "
        cv += "AspectRatioStr = %(AspectRatioStr)s, "
        cv += "Language = %(Language)s, "
        #cv += "OriginalLanguage = %(OriginalLanguage)s, "
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

        sql = u"UPDATE Movie SET "+cv+" WHERE idMovie = '"+str(idMovie)+"'"

        medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)
        # medium_cursor.execute('SET NAMES utf8;')
        # medium_cursor.execute('SET CHARACTER SET utf8;')
        # medium_cursor.execute('SET character_set_database=utf8;')
        medium_cursor.execute(sql,new_movie_row)
        medium_cursor.close()



    # Update genres for this movie

    updated_genres = False

    _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
    _cursor.execute(u"SELECT * FROM MovieGenreView WHERE idMovie='"+str(idMovie)+"'")
    existing_moviegenreview_rowlist = _cursor.fetchall()
    _cursor.close()
    # Columns: idMovieGenre, idMovie, idGenre, GenreName, idGenreType, GenreTypeName, idParentGenre, ParentGenreName,
    #          idSynonymOfGenre, SynonymOfGenreName

    existing_genreid_list = []
    for _row in existing_moviegenreview_rowlist:
        existing_genreid_list.append(_row["idGenre"])

    (new_genreid_list,new_genres) = GetGenreIdList(ss_row, movie_dn)

    if len(existing_genreid_list) == 0 and len(new_genreid_list) == 0:

        pass # no genres; don't report this.

    else:

        existing_genreid_set = set(existing_genreid_list)
        new_genreid_set = set(new_genreid_list)

        if existing_genreid_set ==  new_genreid_set:

            pass # no change

        else:

            # Replace existing genres with new genres

            updated_genres = True

            _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
            _cursor.execute(u"UPDATE Movie SET Genres = '"+utils.SqlLiteral(new_genres)+"' WHERE idMovie='"+str(idMovie)+"'")
            _cursor.close()

            _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
            _cursor.execute(u"DELETE FROM MovieGenre WHERE idMovie='"+str(idMovie)+"'")
            _cursor.close()

            for genreid in new_genreid_list:
                _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
                _cursor.execute(u"INSERT INTO MovieGenre (idMovie, idGenre) VALUES ('"+str(idMovie)+"', '"+str(genreid)+"')")
                _cursor.close()



    # Update persons for this movie

    _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
    _cursor.execute(u"SELECT * FROM MoviePersonView WHERE idMovie='"+str(idMovie)+"'")
    existing_moviepersonview_rowlist = _cursor.fetchall()
    _cursor.close()
    # Columns: idMoviePerson, idMovie, Name, idPersonRoleType, RoleName, RoleDescription

    existing_normalized_actor_name_list = []
    existing_normalized_director_name_list = []
    existing_actor_name_list = []
    existing_director_name_list = []
    for _row in existing_moviepersonview_rowlist:
        if _row["idPersonRoleType"] == 'ACTOR':
            existing_normalized_actor_name_list.append(utils.NormalizeString(_row["Name"]))
            existing_actor_name_list.append(_row["Name"])
        elif _row["idPersonRoleType"] == 'DIRECTOR':
            existing_normalized_director_name_list.append(utils.NormalizeString(_row["Name"]))
            existing_director_name_list.append(_row["Name"])
        # we ignore person types 'MUSIC' and 'AUTHOR' for now

    (new_normalized_director_name_list,new_director_name_list,new_directors) = GetDirectorNameLists(ss_row, movie_dn, ss_layout)
    (new_normalized_actor_name_list,new_actor_name_list,new_actors) = GetActorNameLists(ss_row, movie_dn, ss_layout)

    # Update Directors

    updated_directors = False

    if len(existing_normalized_director_name_list) == 0 and len(new_normalized_director_name_list) == 0:

        pass # no directors; don't report this.

    else:

        existing_normalized_director_name_set = set(existing_normalized_director_name_list)
        new_normalized_director_name_set = set(new_normalized_director_name_list)

        if existing_normalized_director_name_set ==  new_normalized_director_name_set:

            pass # no change

        else:

            # Replace existing directors with new directors

            updated_directors = True

            _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
            _cursor.execute(u"UPDATE Movie SET Directors = '"+utils.SqlLiteral(new_directors)+"' WHERE idMovie='"+str(idMovie)+"'")
            _cursor.close()

            _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
            _cursor.execute(u"DELETE FROM MoviePerson WHERE idMovie='"+str(idMovie)+"' AND idPersonRoleType = 'DIRECTOR'")
            _cursor.close()

            for director_name in new_director_name_list:
                _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
                _cursor.execute(u"INSERT INTO MoviePerson (idMovie, Name, idPersonRoleType) VALUES ('"+str(idMovie)+"', '"+utils.SqlLiteral(director_name)+"', 'DIRECTOR')")
                _cursor.close()

    # Update Actors

    updated_actors = False

    if len(existing_normalized_actor_name_list) == 0 and len(new_normalized_actor_name_list) == 0:

        pass # no actors; don't report this.

    else:

        existing_normalized_actor_name_set = set(existing_normalized_actor_name_list)
        new_normalized_actor_name_set = set(new_normalized_actor_name_list)

        if existing_normalized_actor_name_set ==  new_normalized_actor_name_set:

            pass # no change

        else:

            # Replace existing actors with new actors

            updated_actors = True

            _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
            _cursor.execute(u"UPDATE Movie SET Actors = '"+utils.SqlLiteral(new_actors)+"' WHERE idMovie='"+str(idMovie)+"'")
            _cursor.close()

            _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
            _cursor.execute(u"DELETE FROM MoviePerson WHERE idMovie='"+str(idMovie)+"' AND idPersonRoleType = 'ACTOR'")
            _cursor.close()

            for actor_name in new_actor_name_list:
                _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
                _cursor.execute(u"INSERT INTO MoviePerson (idMovie, Name, idPersonRoleType) VALUES ('"+str(idMovie)+"', '"+utils.SqlLiteral(actor_name)+"', 'ACTOR')")
                _cursor.close()


    if updated_fields or updated_genres or updated_directors or updated_actors:

        utils.Msg("Updated movie: "+movie_dn, verbose_mode)

        if updated_fields:
            for diff_field in diff_field_list:
                utils.Msg("Difference in field "+diff_field+": existing: '"+repr(movie_row[diff_field])+"', new: '"+repr(new_movie_row[diff_field])+"'", verbose_mode)

        if updated_genres:
            utils.Msg("Difference in Genres: existing: "+str(existing_genreid_list)+", new: "+str(new_genreid_list), verbose_mode)

        if updated_directors:
            utils.Msg("Difference in Directors: existing: "+repr(existing_director_name_list)+", new: "+repr(new_director_name_list), verbose_mode)

        if updated_actors:
            utils.Msg("Difference in Actors", verbose_mode)

    else:
        pass # No need to update movie


    movies_conn.commit()


#------------------------------------------------------------------------------
def AddMovie(ss_row, ss_layout):

    global verbose_mode

    colname = colname_m_l_dict[ss_layout]["Title"]
    new_title = ss_row[colname]

    colname = colname_m_l_dict[ss_layout]["ReleaseYear"]
    new_year =  int(ss_row[colname])

    movie_dn = new_title+" ("+str(new_year)+")"

    utils.Msg("Adding movie: "+movie_dn, verbose_mode)

    new_movie_row = GetMovieRow(ss_row, movie_dn, ss_layout)

    c = ""          # column list for INSERT
    v = ""          # value list for INSERT
    c += "Title, "
    v += "%(Title)s, "
    c += "OriginalTitle, "
    v += "%(OriginalTitle)s, "
    c += "SeriesTitle, "
    v += "%(SeriesTitle)s, "
    c += "OriginalSeriesTitle, "
    v += "%(OriginalSeriesTitle)s, "
    c += "EpisodeTitle, "
    v += "%(EpisodeTitle)s, "
    c += "OriginalEpisodeTitle, "
    v += "%(OriginalEpisodeTitle)s, "
    c += "EpisodeId, "
    v += "%(EpisodeId)s, "
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

    sql = u"INSERT INTO Movie ("+c+") VALUES ( "+v+")"

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)

    medium_cursor.execute(sql,new_movie_row)

    medium_cursor.close()


    _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
    _cursor.execute(u"SELECT LAST_INSERT_ID() AS id")
    _rowlist = _cursor.fetchall()
    _cursor.close()
    idMovie = _rowlist[0]["id"]


    # Add genres for this movie

    (new_genreid_list,new_genres) = GetGenreIdList(ss_row, movie_dn)

    _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
    _cursor.execute(u"UPDATE Movie SET Genres = '"+utils.SqlLiteral(new_genres)+"' WHERE idMovie='"+str(idMovie)+"'")
    _cursor.close()

    # Just to be on the safe side...
    _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
    _cursor.execute(u"DELETE FROM MovieGenre WHERE idMovie='"+str(idMovie)+"'")
    _cursor.close()

    for genreid in new_genreid_list:
        _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
        _cursor.execute(u"INSERT INTO MovieGenre (idMovie, idGenre) VALUES ('"+str(idMovie)+"', '"+str(genreid)+"')")
        _cursor.close()


    # Add persons for this movie

    (new_normalized_director_name_list,new_director_name_list,new_directors) = GetDirectorNameLists(ss_row, movie_dn, ss_layout)
    (new_normalized_actor_name_list,new_actor_name_list,new_actors) = GetActorNameLists(ss_row, movie_dn, ss_layout)

    # Just to be on the safe side...
    _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
    _cursor.execute(u"DELETE FROM MoviePerson WHERE idMovie='"+str(idMovie)+"'")
    _cursor.close()

    _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
    _cursor.execute(u"UPDATE Movie SET Directors = '"+utils.SqlLiteral(new_directors)+"' WHERE idMovie='"+str(idMovie)+"'")
    _cursor.close()

    for director_name in new_director_name_list:
        _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
        _cursor.execute(u"INSERT INTO MoviePerson (idMovie, Name, idPersonRoleType) VALUES ('"+str(idMovie)+"', '"+utils.SqlLiteral(director_name)+"', 'DIRECTOR')")
        _cursor.close()

    _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
    _cursor.execute(u"UPDATE Movie SET Actors = '"+utils.SqlLiteral(new_actors)+"' WHERE idMovie='"+str(idMovie)+"'")
    _cursor.close()

    for actor_name in new_actor_name_list:
        _cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
        _cursor.execute(u"INSERT INTO MoviePerson (idMovie, Name, idPersonRoleType) VALUES ('"+str(idMovie)+"', '"+utils.SqlLiteral(actor_name)+"', 'ACTOR')")
        _cursor.close()


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

    global countrycode_de_dict, num_errors

    land_l = land.lower()

    # TBD: Multiple countries as comma separated list not supported

    if land_l in countrycode_de_dict:
        cc = countrycode_de_dict[land_l]
    else:
        utils.ErrorMsg("Did not find country code for country '"+land+"' for movie: "+movie_dn, num_errors)
        cc = None

    return cc


#------------------------------------------------------------------------------
def GetAspectRatio(bildformat,movie_dn):
    # bildformat: aspect ratio, in various formats:
    #             16:9
    #             16x9
    #             1.778
    #             1.778:1
    #             1.778:1 (some text) - any format can be followed by text in parenthesis
    #             None
    # return: tuple:
    #  dar_f: aspect ratio as a float number, e.g. 1.778
    #  dar_s: aspect ratio as a display string, e.g. "16x9"

    global num_errors

    result_delimiter = "x"    # delimiter between width and height to be used in result
    max_dar_failure = 0.02        # max failure for recognizing whole ratios

    # strip off text in parenthesis

    if bildformat != None and bildformat != "":

        bf_pp = bildformat.find("(")
        if bf_pp >= 0:
            bf = bildformat[0:bf_pp].strip(" ")
        else:
            bf = bildformat.strip(" ")

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
                utils.ErrorMsg("Unknown format '"+bildformat+"' for 'bildformat' column (1 dar_f="+str(dar_f)+") of spreadsheet data for movie: "+movie_dn, num_errors)
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
                utils.ErrorMsg("Unknown format '"+bildformat+"' for 'bildformat' column (2 dar_f="+str(dar_f)+") of spreadsheet data for movie: "+movie_dn, num_errors)
                dar_s = str(dar_f)
        else:
            utils.ErrorMsg("Unknown format '"+bildformat+"' for 'bildformat' column of spreadsheet data for movie: "+movie_dn, num_errors)
            dar_s = bf
            dar_f = None
    else:
            dar_s = None
            dar_f = None

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
    u"de": "de",
    u"ar": "ar",
    u"en": "en",
    u"fr": "fr",
    u"es": "es",
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

        if abs(failure) <= max_failure:
            eq = True
        else:
            eq = False

    return eq


#------------------------------------------------------------------------------
def GetLanguageCode(sprache,movie_dn):

    global languagecode_de_dict, num_errors

    if sprache == None or sprache == "":
        lc = None

    else:
        sprache_l = sprache.lower()

        if sprache_l in languagecode_de_dict:
            lc = languagecode_de_dict[sprache_l]
        else:
            utils.ErrorMsg("Did not find language code for language '"+sprache+"' for movie: "+movie_dn, num_errors)
            lc = None

    return lc


#------------------------------------------------------------------------------
def GetIdVideoQuality(name, file):

    global idvideoquality_dict, num_errors

    if name in idvideoquality_dict:
        id = idvideoquality_dict[name]
    else:
        id = None
        utils.ErrorMsg("Video quality name '"+name+"' not found in movie database, file: "+file, num_errors)

    return id

#------------------------------------------------------------------------------
def GetIdContainerFormat(field_value, file):

    global idcontainerformat_dict, num_errors

    if field_value in idcontainerformat_dict:
        id = idcontainerformat_dict[field_value]
    else:
        id = None
        utils.ErrorMsg("Container format field value '"+field_value+"' not found in movie database, file: "+file, num_errors)

    return id

#------------------------------------------------------------------------------
def GetIdVideoFormat(format_field_value, profile_field_value, file):

    global fixedvideoformat_list, num_errors

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
        utils.ErrorMsg("Video format field value '"+format_field_value+"' and profile field value '"+str(profile_field_value)+"' not found in movie database, file: "+file, num_errors)

    return id

#------------------------------------------------------------------------------
def GetIdAudioFormat(format_field_value, profile_field_value, file):

    global fixedaudioformat_list, num_errors

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
        utils.ErrorMsg("Audio format field value '"+format_field_value+"' and profile field value '"+str(profile_field_value)+"' not found in movie database, file: "+file, num_errors)

    return id

#------------------------------------------------------------------------------
def GetIdVideoFramerateMode(field_value, file):

    global idvideoframeratemode_dict, num_errors

    if field_value in idvideoframeratemode_dict:
        id = idvideoframeratemode_dict[field_value]
    else:
        id = None
        utils.ErrorMsg("Video framerate mode field value '"+field_value+"' not found in movie database, file: "+file, num_errors)

    return id

#------------------------------------------------------------------------------
def GetIdAudioBitrateMode(field_value, file):

    global idaudiobitratemode_dict, num_errors

    if field_value in idaudiobitratemode_dict:
        id = idaudiobitratemode_dict[field_value]
    else:
        id = None
        utils.ErrorMsg("Audio bitrate mode field value '"+field_value+"' not found in movie database, file: "+file, num_errors)

    return id

#------------------------------------------------------------------------------
def GetIdCabinet(smb_server_resource, file):

    global idcabinet_dict, num_errors

    if smb_server_resource in idcabinet_dict:
        id = idcabinet_dict[smb_server_resource]
    else:
        id = None
        utils.ErrorMsg("Media cabinet for SMB server resource '"+smb_server_resource+"' not found in movie database, file: "+file, num_errors)

    return id


#------------------------------------------------------------------------------
# main routine
#


num_errors = 0                  # global number of errors
ss_file    = None               # spreadsheet file path
ss_sheet   = None               # spreadsheet sheet name
ss_layout  = None               # layout of data in sheet
verbose_mode = False            # verbose mode, controlled by -v option
update_all = False              # Update all movies, instead of just those whose records are outdated, controlled by -a option

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
        elif arg == "-f":
            _i += 1
            if _i == len(sys.argv):
                utils.ErrorMsg("Missing file parameter for -f option")
                exit(100)
            ss_file = sys.argv[_i]
        elif arg == "-s":
            _i += 1
            if _i == len(sys.argv):
                utils.ErrorMsg("Missing sheet parameter for -s option")
                exit(100)
            ss_sheet = sys.argv[_i]
        elif arg == "-l":
            _i += 1
            if _i == len(sys.argv):
                utils.ErrorMsg("Missing layout parameter for -l option")
                exit(100)
            ss_layout = sys.argv[_i]
        elif arg == "-a":
            update_all = True
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
if ss_file == None:
    utils.ErrorMsg("Required option not specified: -f file")
    exit(100)

if ss_sheet == None:
    utils.ErrorMsg("Required option not specified: -s sheet")
    exit(100)

if ss_layout == None:
    utils.ErrorMsg("Required option not specified: -l layout")
    exit(100)

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


# Read the spreadsheet

ss_path, ss_ext = os.path.splitext(ss_file)
ss_ext = ss_ext.lower()

if ss_ext == ".xls":

    try:
        ss_xls = xlrd.open_workbook(ss_file)
    except Exception as exc:
        utils.ErrorMsg("Cannot open Excel spreadsheet for reading: "+repr(ss_file)+", "+repr(exc), num_errors)
        exit(12)

    _sheet = ss_xls.sheet_by_name(ss_sheet)
    ss_rowlist = []
    col_titlelist = []
    for rowx in range(_sheet.nrows):
        if rowx == 0:
            # The first row contains the column names
            for colx in range(_sheet.ncols):
                col_title = _sheet.cell(rowx,colx).value
                col_titlelist.append(col_title)
        else:
            ss_row = dict()
            for colx in range(_sheet.ncols):
                ss_row[col_titlelist[colx]] = _sheet.cell(rowx,colx).value
            ss_rowlist.append(ss_row)

    ss_xls.release_resources() # closes the file

elif ss_ext == ".ods" and False: # currently disabled because ezodf works only for Python 3.x

    ss_ods = ezodf.opendoc(ss_file)
    try:
        ss_ods = ezodf.opendoc(ss_file)
    except Exception as exc:
        print "Debug: exc="+repr(exc)
        utils.ErrorMsg("Cannot open ODS spreadsheet for reading: "+repr(ss_file)+", "+repr(exc), num_errors)
        exit(12)

    _sheet = ss_ods.sheet[ss_sheet]
    ss_rowlist = []
    col_titlelist = []
    # The first row contains the column names
    for _cell in _sheet.row(0):
        _title = _cell.value
        col_titlelist.append(_title)
    for _row in _sheet.rows():
        ss_row = dict()
        for _colx in range(_row.ncols()):
            ss_row[col_titlelist[_colx]] = _row(colx).value
        ss_rowlist.append(ss_row)

    print "Debug: "+repr(ss_rowlist)

    # ezdoc does not seem to provide a way to close the file

elif ss_ext == ".csv":

    try:
        ss_csv = UnicodeReader(open(ss_file, 'rb'), encoding="utf-8", delimiter=',', quotechar='"', doublequote=True)
    except Exception as exc:
        utils.ErrorMsg("Cannot open CSV spreadsheet for reading: "+repr(ss_file)+", "+repr(exc), num_errors)
        exit(12)

    ss_rowlist = []
    col_titlelist = []
    rowx = 0
    for row in ss_csv:
        if rowx == 0:
            # The first row contains the column names
            for col in row:
                bom = hex(ord(col[0]))
                if hex(ord(col[0])) == "0xfeff":  # remove BOM (somewhat quirky ...)
                    col = col[1:].strip('"')
                col_titlelist.append(col)
        else:
            ss_row = dict()
            colx = 0
            for col in row:
                ss_row[col_titlelist[colx]] = col
                colx += 1
            ss_rowlist.append(ss_row)
        rowx += 1

    # Todo: close spreadsheet file

else:
    utils.ErrorMsg("Invalid spreadsheet file extension: "+ss_ext)
    exit(12)

utils.Msg("Found "+str(len(ss_rowlist))+" movies in spreadsheet: "+repr(ss_file))


# Read the movie descriptions

_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute(u"SELECT * FROM Movie")
movie_rowlist = _cursor.fetchall()
_cursor.close()

utils.Msg("Found "+str(len(movie_rowlist))+" movie descriptions in movie database (Movie table)")


_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute(u"SELECT * FROM Genre")
genre_rowlist = _cursor.fetchall()
_cursor.close()


movies_conn.commit()


# Build dictionaries of Genre table, for fast access

genre_gid_dict = dict()     # dictionary of known movie genres with access by genre id
                            # key: genre id (idGenre column of Genre table)
                            # value: index into genre_rowlist, 0-based
i = 0
for genre_row in genre_rowlist:
    idGenre = genre_row["idGenre"]
    genre_gid_dict[idGenre] = i
    i += 1

genre_nname_dict = dict()   # dictionary of known movie genres with access by normalized genre name
                            # key: normalized genre name (Name column of Genre table, normalized)
                            # value: index into genre_rowlist, 0-based
i = 0
for genre_row in genre_rowlist:
    genrenname = utils.NormalizeString(genre_row["Name"])
    genre_nname_dict[genrenname] = i
    i += 1


# Build dictionary of current Movie table, for fast access

movie_tn_y_dict = dict()     # dictionary of movies with access by normalized title + year
                            # key: normalized title '#' release year
                            # value: index into movie_rowlist array (0-based)

i = 0
for movie_row in movie_rowlist:

    title_normalized = utils.NormalizeTitle(movie_row["Title"])
    year = int(movie_row["ReleaseYear"])

    if year == None:
        utils.ErrorMsg("Movie database inconsistency: Movie with id "+str(movie_row["idMovie"])+\
                       " has no release year: '"+movie_row["Title"]+"'", num_errors)
        # TBD: Update existing movie entry instead of ignoring the existing entry and adding a new one.
    else:

        tn_y_key = title_normalized + "#" + str(year)
        if tn_y_key in movie_tn_y_dict:
            existing_movie_row = movie_rowlist[movie_tn_y_dict[tn_y_key]]
            existing_movie_dn = existing_movie_row["Title"] + " (" + str(int(existing_movie_row["ReleaseYear"])) + ")"
            movie_dn = movie_row["Title"] + " (" + str(int(movie_row["ReleaseYear"])) + ")"
            utils.ErrorMsg("Movie database inconsistency: Movie with id "+str(movie_row["idMovie"])+\
                           " is a duplicate of movie with id "+str(existing_movie_row["idMovie"])+": '"+movie_dn+"'", num_errors)
        else:
            movie_tn_y_dict[tn_y_key] = i

    i += 1


# Copy the spreadsheet data into the Movie table, replacing movies that already exist

utils.Msg("Updating movie descriptions from spreadsheet ...")

ss_tn_y_dict = dict()     # dictionary of movies in spreadsheet, with access by normalized title + year
                                  # key: normalized title '#' release year
                                  # value: index into ss_rowlist array (0-based)

i = 0
for ss_row in ss_rowlist:

    # Try to match the new movie by normalized title and year

    colname = colname_m_l_dict[ss_layout]["Title"]
    new_title = ss_row[colname]

    colname = colname_m_l_dict[ss_layout]["ReleaseYear"]
    new_year =  int(ss_row[colname])

    new_title_normalized = utils.NormalizeTitle(new_title)

    # We need to ensure that the resulting Movie rows have a release year,
    # so we reject any import row that does not have a release year.

    if new_year == None:

        utils.ErrorMsg("Skipping movie in spreadsheet that does not have a release year: "+new_title, num_errors)

    else:

        tn_y_key = new_title_normalized + "#" + str(new_year)

        # Check if the movie exists in the Movie table
        # TBD: Add other ways to match the movie

        if tn_y_key in movie_tn_y_dict:

            movie_row = movie_rowlist[movie_tn_y_dict[tn_y_key]]
            UpdateMovie(ss_row, movie_row, ss_layout)

        else:

            AddMovie(ss_row, ss_layout)

        # Check for duplicates

        if tn_y_key in ss_tn_y_dict:
            ss_dn = new_title_normalized + " (" + str(new_year) + ")"
            utils.ErrorMsg("Spreadsheet data inconsistency: Multiple movies with same title and year: "+ss_dn, num_errors)
        else:
            ss_tn_y_dict[tn_y_key] = i

    i += 1


if num_errors > 0:
    utils.ErrorMsg("Finished with "+str(num_errors)+" errors.")
    exit(12)
else:
    utils.Msg("Success.")
    exit(0)
