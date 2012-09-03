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


import re, string, sys, subprocess, os, os.path, fnmatch, time


#------------------------------------------------------------------------------
def ErrorMsg(msg, num_errors=None):
    """Prints an error message to stdout and increases number of errors by 1.

    Parameters:
        msg:        Message string (str or unicode type).
                    The string "Error: " gets added to the message string.
        num_errors: Integer with number of errors.

    Returns nothing
    """

    msg = "Error: "+msg

    _PrintMsg(msg)

    if num_errors != None:
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

    _PrintMsg(msg)

    return


#------------------------------------------------------------------------------
def Msg(msg, verbose_mode=True):
    """Prints a message to stdout if in verbose mode.

    Parameters:
        msg:        Message string (str or unicode type).
        verbose_mode:   Boolean indicating whether in verbose mode.

    Returns nothing
    """

    if verbose_mode:
        _PrintMsg(msg)

    return


#------------------------------------------------------------------------------
def _PrintMsg(msg):
    """Prints a message to stdout.

    Parameters:
        msg:        Message string (str or unicode type).

    Returns nothing
    """

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
def NormalizeString(ustr):
    # _str is a unicode string

    global _normalize_utrans_table

    if ustr == None:
        nstr = None
    else:
        nstr = ustr
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


#------------------------------------------------------------------------------
def SqlLiteral(_str):
    # _str is a (unicode) string for use in a SQL literal

    nstr = _str
    nstr = nstr.replace("'","\\'")

    return nstr


#------------------------------------------------------------------------------
def RunCmd(cmd, timeout=None):
    """Execute a command under timeout control and return its standard output, standard
    error and exit code.
    The command is executed using a shell.

    Parameters:
        cmd         Command to execute, as a single string of type str or unicode.
                    If passed as unicode, then the command string is encoded to str
                    using the file system encoding (typically 'mbcs'), because
                    Python 2.x does not currently support the unicode version of Windows
                    CreateProcess().
        timeout     Timeout in seconds, None means no timeout.

    Returns:
        Tuple:
            stdout string (str)
            stderr string (str)
            exit code (int)
        The encoding of stdout and stderr is sys.stdout.encoding unless that is None (when
        redirected) in which case probably(!) the file system encoding is used
        (sys.getfilesystemencoding()).

    Exceptions:
        OSError (errno, strerror), if command execution fails.
        TypeError (str), if the command parameter did not have one of the expected types.
        Exception (str), if the timeout was reached.
    """

    stdout_str = None   # stdout string of command
    stderr_str = None   # stderr string of command
    exit_code = None    # exit code of command

    # Make sure the command is passed as type str. If we pass it as unicode, then
    # it gets encoded using 'ascii' which is worse than encoding it here with the
    # file system encoding (typically 'mbcs'). That is still not perfect though.
    # The ideal fix would be that Python uses the Unicode version CreateProcessW()
    # in PC/_subprocess.c.
    if type(cmd) == unicode:
        cmd = cmd.encode(sys.getfilesystemencoding())
    elif type(cmd) != str:
        raise TypeError("Invalid type of cmd parameter: "+str(type(cmd)))

    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    if not timeout:
        # no timeout set, wait unlimited for process to complete

        exit_code = p.wait()

    else:
        # timeout set, perform soft polling for command completion

        fin_time = time.time() + timeout
        while p.poll() == None and  time.time() < fin_time:
            time.sleep(0.2)

        # if timeout reached, raise an exception
        if  time.time() > fin_time:
            p.kill()
            raise Exception("Process timeout has been reached")

        exit_code = p.returncode

    stdout_str, stderr_str = p.communicate()          # Retrieves pipe output, as type str

    return stdout_str, stderr_str, exit_code


#------------------------------------------------------------------------------
def RecursiveGlob(directory, fnpattern):
    """Find files in a directory subtree that match a file name pattern.
    The case sensitivity of the file pattern matching is OS-specific (e.g. case insensitive on Windows).
    Symbolic links are not being followed.
    If the directory parameter is passed as type unicode, the resulting filenames will also be of type unicode.

    Parameters:
        directory       Path name of root of directory subtree to be searched (absolute or relative).
        fnpattern       File name pattern, using OS-specific wildcards (e.g. "?" and "*").

    Returns:
        List of matching file names, with fully qualified path name.
    """

    filenames = []
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, fnpattern):
                filenames.append(os.path.join(root, basename))

    return filenames


#------------------------------------------------------------------------------
class ParseError (BaseException):
    '''Parse error exception.'''


#------------------------------------------------------------------------------
def ParseMovieFilename(filename,tolerate_noext=False):
    '''Parse the file name of a movie file and return the information as a dictionary.

    Parameters:
        filename        Base file name of movie file (file.ext), as unicode type, in the
                        following format.
        tolerate_noext  Boolean indicating that missing file extension is being tolerated.
                        This is used for parsing title tags in movie files.

    File name format:
        Syntax used for format description:
            {} surround variables
            [] surround optional parts
        Format:
            {complextitle}([3D ][{lang} ]{q} {dar}[ {techcomm}])[.{dup}][.{partial}][.uncut].{ext}
        Where:
            {complextitle}  Complex title in the file name. May contain "[text]", "(text)", "(year)",
                            episode numbers, series and episode titles.
                            Should be parsed with ParseComplexTitle().
            Quality block (mandatory, in parenthesis):
                3D          Optional: Presence indicates that the movie is some sort of 3D movie.
                {lang}      Optional: Language of the audio stream in the movie and language of any subtitles.
                            Must be in format: {lang}[-U[-{lang}]]
                            where {lang} is a 2- or 3-char language code.
                            For example: "en", "fr-U", "ar-U-fr".
                            Presence of "-U" indicates that the movie has subtitles (Untertitel).
                            The default language is "de", both of the audio stream and of the subtitles.
                            It is not currently supported to have more than one audio stream per media file
                            (e.g. for different languages).
                {q}         Mandatory: Keyword indicating quality.
                            Must not contain blanks or parenthesis.
                            For example: "HD", "HQ", "SD", "HQ-low", "HD+SD", etc..
                {dar}       Mandatory: Desired display aspect ratio.
                            Must be in format: {integer]x{integer}.
                            For example: "16x9", "4x3"
                {techcomm}  Optional: Technical comments on the movie.
                            Must not contain parenthesis.
                            For example: "size varies"
           {dup}            Duplication number (to distinguish duplicates).
                            Must be an integer, usually starting with "2".
           {partial}        Partial indicator. Presence indicates that the movie file contains only the
                            specified part of the entire movie.
                            Must not contain blanks, dots or parenthesis.
                            For example: "missing-end" indicates that the file contains everything but the end.
           uncut            Presence indicates that the movie is not yet cut (i.e. contains advertisements, or
                            extra content at begin or end)
           {ext}            File extension, indicates the container format.
                            Must be one of: "mp4", "divx.avi", "mpg.avi"
                            A missing file extension is tolerated if tolerate_noext is True.

    Returns:
        If the filename could be parsed, returns a dictionary with information from the movie file name:
            "complex_title" Complex title in the file name, as unicode type.
            "3d"            Boolean indicating whether the movie is some sort of 3D movie.
            "audio_lang"    Language code of the audio stream in the movie, as str type (e.g. "de").
                            If the file name does not indicate a language for the audio stream, the
                            default "de" is returned.
            "subtitle_lang" Language code of the subtitles in the movie, if any, as a string.
                            If the movie does not have subtitles, this value is None.
                            If the file name indicates that the movie has subtitles but no language for them,
                            the default "de" is returned.
            "quality"       Quality of the movie, as a str type, using the following values:
                                "HD", "HQ", "SD", "HQ-low", "HD+SD", etc.
            "dar_w"         Width component of desired display aspect ratio, as a string.
            "dar_h"         Height component of desired display aspect ratio, as a string.
            "tech_comm"     Technical comments on the movie (e.g. "contains pixels"), as a string.
            "dup"           Duplication number of the movie file (e.g. "2"), as a string.
            "partial"       Keyword indicating that the movie file contains only a part of the movie,
                            as a string (e.g. "missing-end")
            "uncut"         Boolean indicating whether the movie is not yet cut.
            "container"     Indicator for container format, as str type, using the following list:
                                "MP4", "DIVX AVI", "MPG AVI"
                            None, if tolerate_noext is True and the file extension was missing.

        If the filename could not be parsed, raises a ParseError exception with an error message stating the issue.
    '''

    # print "Debug: ParseMovieFilename: filename: \""+repr(filename)+"\""

    rv = dict()         # return value dictionary, see description.

    qblock_end_pos = filename.rfind(")")            # 0-based position of ending ")" of quality block
    if qblock_end_pos == -1:
        raise ParseError(u"Cannot find end of quality block in movie file name: \""+filename+"\"")

    filename_part1 = filename[0:qblock_end_pos+1]   # first part of filename, up to ending ")" of quality block
    filename_part2 = filename[qblock_end_pos+1:]    # remaining part of filename

    qblock_beg_pos = filename_part1.rfind("(")      # 0-based position of starting "(" of quality block
    if qblock_beg_pos == -1:
        raise ParseError(u"Cannot find begin of quality block in movie file name: \""+filename+"\"")

    # Determine complex title
    rv["complex_title"] = filename_part1[0:qblock_beg_pos].strip(" ")   # everything before quality block


    # Parse the quality block, as blank-separated words from left to right

    qblock = filename_part1[qblock_beg_pos+1:len(filename_part1)-1]     # quality block, without ()
    qblock_words = qblock.strip(" ").split(" ")

    # Determine 3D indicator
    if qblock_words[0] == "3D":
        rv["3d"] = True
        qblock_words = qblock_words[1:]
    else:
        rv["3d"] = False

    # Determine language indicators (including subtitles)
    m = re.match("([a-z]{2,3})(-U(?:-([a-z]{2,3}))?)?",qblock_words[0])
    if m != None:
        rv["audio_lang"] = m.group(1)               # The specified audio language
        _gl = len(m.groups())
        if _gl == 1: # just the audio language specified, no -U
            rv["subtitle_lang"] = None              # No subtitles
        elif _gl == 2: # -U specified without subtitle language
            rv["subtitle_lang"] = "de"              # The default subtitle language
        else: # -U specified with subtitle language
            rv["subtitle_lang"] = m.group(2)        # The specified subtitle language
        qblock_words = qblock_words[1:]
    else:
        rv["audio_lang"] = "de"                     # The default audio language
        rv["subtitle_lang"] = None                  # No subtitles

    # Determine quality
    rv["quality"] = qblock_words[0]
    qblock_words = qblock_words[1:]

    # Determine desired display aspect ratio
    m = re.match(r"^([0-9]+)x([0-9]+)$",qblock_words[0])
    if m != None:
        rv["dar_w"] = m.group(1)
        rv["dar_h"] = m.group(2)
    else:
        raise ParseError(u"Invalid display aspect ratio \""+qblock_words[0]+"\" in movie file name: \""+filename+"\"")
    qblock_words = qblock_words[1:]

    # Determine technical comments
    if len(qblock_words) > 0:
        rv["tech_comm"] = " ".join(qblock_words[0:])
    else:
        rv["tech_comm"] = None


    # Parse the remaining filename, as dot-separated words from right to left

    part2_words = filename_part2.strip(".").split(".")

    # Determine container format
    if filename_part2.endswith(".mp4"):
        rv["container"] = "MP4"
        part2_words = part2_words[0:-1]
    elif filename_part2.endswith(".divx.avi"):
        rv["container"] = "DIVX AVI"
        part2_words = part2_words[0:-2]
    elif filename_part2.endswith(".mpg.avi"):
        rv["container"] = "MPG AVI"
        part2_words = part2_words[0:-2]
    else:
        if tolerate_noext:
            rv["container"] = None
        else:
            raise ParseError(u"Unknown file extension in movie file name: \""+filename+"\"")

    # Determine uncut indicator
    rv["uncut"] = False
    if len(part2_words) > 0:
        if part2_words[-1] == "uncut":
            rv["uncut"] = True
            part2_words = part2_words[0:-1]

    # Determine duplication number (left-most of remaining words)
    rv["dup"] = None
    if len(part2_words) > 0:
        m = re.match(r"^([0-9]+)$",part2_words[0])
        if m != None:
            rv["dup"] = m.group(1)
            part2_words = part2_words[1:]

    # Determine partial indicator (left-most of remaining words)
    rv["partial"] = None
    if len(part2_words) > 0:
        rv["partial"] = part2_words[0]
        part2_words = part2_words[1:]

    if len(part2_words) > 0:
        raise ParseError(u"Superflous component after quality block in movie file name: \""+filename+"\"")

    # print "Debug: ParseMovieFilename: Return: "+repr(rv)

    return rv


#------------------------------------------------------------------------------
def ParseComplexTitle(complex_title):
    '''Parse the complex title of a movie and return the information as a dictionary.

    Parameters:
        complex_title       Complex title, as unicode type, in the following format.

    Complex title format:
        1. Optional bracket text is determined and removed: Up to one occurrence of "[text]".
        2. Optional release year is determined and removed: Rightmost occurrence of "(NNNN)".
        3. Remaining complex title text must have one of the following formats (for syntax, see ParseFilename):
            {title}
            {series_title}( - |, ){ep_id}[ - {ep_title}]
       Where:
            {title}         Title of movie that is not an episode of a series.
                            Must not contain " - ".
            {series_title}  Title of movie series this movie is an episode of.
                            Must not contain " - " or ", ".
            {ep_title}      Title of this episode.
                            May contain " - " or ", ".
            {ep_id}         Identifier for this episode, in one of the following formats:
                                {seq_id}             Sequential identifier of episode within the whole series
                                {sea_id}.{sep_id}    Identifiers for season, and for episode within season.
                                {seq_main_id}-{seq_sub_id}    Sequential identifier of episode within the whole series,
                                                     consisting of main identifier and sub identifier.
                                {part_key} {seq_id}  Sequential identifier of episode within the whole series,
                                                     with part_key being some keyword such as "Part", "Teil", "Folge".
                            Typically these identifiers are integer numbers, but they can also be text.
                            Each {*_id} part must not contain blanks, dots or minuses.

    Returns:
        If the complex title could be parsed, returns a dictionary with information from the title:
            "bracket_text"  Text in square brackets (without the brackets), as unicode type.
                            None, if no bracket text was present.
            "year"          Release year of the movie, as a string.
                            None, if no release year was specified.
            "clean_title"   Title without bracket text and release year (for both episodes and other movies).
            "series_title"  For a title that is an episode of a series, the series title.
                            Otherwise, None.
            "episode_title" For a title that is an episode of a series, the episode title.
                            Otherwise, or if there is no episode title specified, None.
            "episode_id"    For a title that is an episode of a series, the identifier for this episode,
                            matching {ep_id} in the syntax definition.
                            Otherwise, None.
                            Examples: "1", "01", "1.07", "01.07", "S.1a", "217a", "Folge 2", "part 1.1", "Spezial 2012-08-25"

        If the complex title could not be parsed, raises a ParseError exception with an error message stating the issue.
    '''

    # print "Debug: ParseComplexTitle: complex_title: \""+repr(complex_title)+"\""

    rv = dict()         # return value dictionary, see description.

    # Determine and remove bracket text
    m = re.match("^(.*)\[(.*?)\](.*)$",complex_title)
    if m != None:
        rv["bracket_text"] = m.group(2).strip(" ")
        complex_title = m.group(1).strip(" ") + " " + m.group(3).strip(" ")
    else:
        rv["bracket_text"] = None

    # Determine and remove release year
    m = re.match("^(.*)\(([0-9]{4})\)(.*)$",complex_title)
    if m != None:
        rv["year"] = m.group(2)
        complex_title = m.group(1).strip(" ") + " " + m.group(3).strip(" ")
    else:
        rv["year"] = None

    rv["clean_title"] = complex_title

    # Determine whether title is episode
    rv["series_title"] = None
    rv["episode_id"] = None
    rv["episode_title"] = None
    m = re.match("^(.+?)(?: - |, )(.+?)(?: - (.+))?$",complex_title)
    if m != None:
        possible_episode_id = m.group(2).strip(" ")
        m2 = re.match("^([^ .\-]+([.\-][^ .\-]+)?|[A-za-z]+ [0-9\.-]+)$",possible_episode_id)
        if m2 != None:
            # Movie is an episode
            rv["series_title"] = m.group(1).strip(" ")
            rv["episode_id"] = possible_episode_id
            if m.group(3) != None:
                rv["episode_title"] = m.group(3).strip(" ")
            else:
                rv["episode_title"] = None

    # print "Debug: ParseComplexTitle: Return: "+repr(rv)

    return rv


#------------------------------------------------------------------------------
