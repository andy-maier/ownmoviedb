#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
# coding: utf-8
#
# Module with utility functions for movies project.
#
# Supported platforms:
#   Runs on any OS platform that has Python 2.7.
#   Tested on Windows XP.
#
# Prerequisites:
#   1. Python 2.7, available from http://www.python.org
#
# Change log:
#   V1.0.0 2012-07-22
#     Added support for MediaInfo 0.7.58, by changing --output=xml to --output=XML
#     Added U+00AA and U+0152 to xmlrep_trans translation list to fix issue with invalid XML produced by MediaInfo.

__version__ = "1.0.0"

import re, string

#------------------------------------------------------------------------------
# Translation table for normalizing strings for comparison
_normalize_utrans_table = [
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

    global _normalize_utrans_table

    if _str == None:
        nstr = None
    else:
        nstr = _str
        for fm_ord,to_str in _normalize_utrans_table:
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


