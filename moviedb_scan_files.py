#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
# coding: utf-8
#
# Updates media information in movie database from movie files.
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
#   V1.0.3 2012-06-24
#     Added support for MediaInfo 0.7.58, by changing --output=xml to --output=XML
#     Added U+00AA and U+0152 to xmlrep_trans translation list to fix issue with invalid XML produced by MediaInfo.
#   V1.0.5 2012-08-13
#     Moved file_sources to movies_config.
#   V1.2.0 2012-09-02
#     Renamed package to moviedb and restructured modules.
#   V1.3.0 2012-12-26
#     Added support for FolderPath column.
#   V1.4.0 2013-09-09
#     Added support for more than one audio stream.

import re, sys, glob, os, os.path, string, errno, locale, fnmatch, subprocess, xml.etree.ElementTree, datetime
from operator import itemgetter, attrgetter, methodcaller
import MySQLdb
from moviedb import config, utils, version


#------------------------------------------------------------------------------
def Usage ():
    """Print the command usage to stdout.
       Input:
         n/a
       Return:
         void.
    """

    global my_name

    print ""
    print "Scans movie files and updates media information in movie database."
    print "The media records in the movie database will be removed, added or updated, as needed."
    print ""
    print "Usage:"
    print "  "+my_name+" [options]"
    print ""
    print "Options:"
    print "  -a          Update all movies, instead of just those whose records are outdated."
    print "  -v          Verbose mode: Display additional messages."
    print "  -h, --help  Display this help text."
    print ""
    print "Movie database being updated:"
    print "  MySQL host: "+config.MYSQL_HOST+" (default port 3306)"
    print "  MySQL user: "+config.MYSQL_USER+" (no password)"
    print "  MySQL database: "+config.MYSQL_DB
    print ""
    print "Locations of movie files being scanned (including subdirectories):"
    for file_source in config.FILE_SOURCES:
        print "  "+file_source["res"]+file_source["dir"]
    print ""

    return


#------------------------------------------------------------------------------
def GetMovieInfo(moviefile_uncpath):
    """Get information about a movie file.

    Parameters:
        moviefile_uncpath:  UNC file path of the movie file (with Windows separators, as unicode type)

    Returns:
        dictionary with information about the file. See code for details.
    """

    global num_errors, verbose_mode

    basefile = os.path.basename(moviefile_uncpath)

    # Split file path into UNC resource name and local file path
    _spos = moviefile_uncpath.find("\\",2)         # 0-based position of first backslash after initial "\\" (i.e. between server and share name)
    _ppos = moviefile_uncpath.find("\\",_spos+1)   # 0-based position of backslash that separates UNC resource name and local file path
    if moviefile_uncpath[0:2] == "\\\\" and _spos > 0 and _ppos > 0:
        res = moviefile_uncpath[0:_ppos]         # UNC resource name (e.g. \\192.168.0.12\share)
        path = moviefile_uncpath[_ppos:]         # local file path on the UNC resource, with leading backslash
    else:
        utils.ErrorMsg("Skipping file: File path does not start with UNC resource name: "+moviefile_uncpath, num_errors)
        return None

    try:
        parsed_filename = utils.ParseMovieFilename(basefile)
    except utils.ParseError as exc:
        utils.ErrorMsg(u"Skipping file: "+unicode(exc))
        return None

    try:
        parsed_complex_title = utils.ParseComplexTitle(parsed_filename["complex_title"])
    except utils.ParseError as exc:
        utils.ErrorMsg(u"Skipping file: "+unicode(exc))
        return None

    movie = dict()

    # These values are defaults from the file name and will be overridden from the title tag, if present.
    movie["title"] = parsed_complex_title["title"]
    movie["year"] = parsed_complex_title["year"]
    movie["series_title"] = parsed_complex_title["series_title"]
    movie["episode_title"] = parsed_complex_title["episode_title"]
    movie["episode_id"] = parsed_complex_title["episode_id"]
    movie["status"] = sourcepath_dict[moviefile_uncpath]["status"]

    # These values remain
    movie["fn_uncut"] = "1" if parsed_filename["uncut"] else "0"
    movie["fn_container_format"] = parsed_filename["container"]
    movie["fn_threed"] = parsed_filename["3d"]
    movie["fn_language"] = parsed_filename["audio_lang"]
    movie["fn_subtitle_language"] = parsed_filename["subtitle_lang"]
    movie["fn_quality"] = parsed_filename["quality"]
    movie["idVideoQuality"] = GetIdVideoQuality(parsed_filename["quality"], moviefile_uncpath)
    movie["fn_dar_width"] = parsed_filename["dar_w"]
    movie["fn_dar_height"] = parsed_filename["dar_h"]
    movie["fn_techcomm"] = parsed_filename["tech_comm"]
    movie["fn_partial"] = parsed_filename["partial"]
    movie["file_res"] = res
    movie["file_path"] = path
    movie["folder_path"] = sourcepath_dict[moviefile_uncpath]["folder_path"]
    movie["idCabinet"] = GetIdCabinet(res, moviefile_uncpath)


    # Invoke MediaInfo on the file.
    # We use specify a timeout, because in the past, MediaInfo due to a bug sometimes ran very long.
    start_time = datetime.datetime.now()

    try:
        mediainfo_xml_str, _stderr_str, _exit_code = utils.RunCmd("mediainfo_cli --output=XML \""+moviefile_uncpath+"\"", timeout=300)
        # RunCmd returns stdout and stderr as str typed strings.
        rc = 0
    except OSError as (errno, strerror):
        utils.ErrorMsg("Missing media info: Cannot call mediainfo_cli: "+strerror, num_errors)
        rc = -1
    except Exception as exc:
        utils.ErrorMsg(u"Missing media info: Error when calling mediainfo_cli: "+unicode(exc), num_errors)
        rc = -1

    end_time = datetime.datetime.now()
    mediainfo_duration = (end_time - start_time).total_seconds()

    if mediainfo_duration > 30:
        utils.Msg("Large mediainfo_cli execution time of "+str(round(mediainfo_duration))+" s for file: \""+moviefile_uncpath+"\"")

    movie["duration_min"] = None
    movie["container_format"] = None
    movie["idContainerFormat"] = None
    movie["video_format"] = None
    movie["video_format_profile"] = None
    movie["idVideoFormat"] = None
    movie["video_bitrate_kbps"] = None
    movie["video_width"] = None
    movie["video_height"] = None
    movie["video_dar"] = None
    movie["video_dar_org"] = None
    movie["video_framerate_fps"] = None
    movie["video_framerate_mode"] = None
    movie["idVideoFramerateMode"] = None
    movie["audio_format"] = None
    movie["audio_format_profile"] = None
    movie["idAudioFormat"] = None
    movie["audio_bitrate_kbps"] = None
    movie["audio_bitrate_mode"] = None
    movie["idAudioBitrateMode"] = None
    movie["audio_samplingrate_hz"] = None


    if rc == 0:

        # Replace invalid characters and invalid numeric character references (00..1F except 09 0D 0A),
        # because the Expat parser used by ElementTree rejects such invalid characters.

        def char_repl(matchobj):
            ucscode = ord(matchobj.group(1))
            repl = "\\u"+format(ucscode,"04x")
            # utils.WarningMsg("Replaced invalid character U+"+format(ucscode,"04X")+" with string '"+\
            #                  repl+"' in MediaInfo XML output.")
            return repl

        def dec_ref_repl(matchobj):
            ucscode = int(matchobj.group(1))
            repl = "\\u"+format(ucscode,"04x")
            # utils.WarningMsg("Replaced invalid character reference &#"+format(ucscode,"03d")+" with string '"+\
            #                  repl+"' in MediaInfo XML output.")
            return repl

        def hex_ref_repl(matchobj):
            ucscode = int(matchobj.group(1),16)
            repl = "\\u"+format(ucscode, "04x")
            # utils.WarningMsg("Replaced invalid character reference &#x0"+format(ucscode,"02x")+" with string '"+\
            #                  repl+"' in MediaInfo XML output.")
            return repl

        mediainfo_xml_u = mediainfo_xml_str.decode("utf-8","replace")

        invalid_char_match = u'(\u0000|\u0001|\u0002|\u0003|\u0004|\u0005|\u0006|\u0007|\u0008|\u000b|\u000c|\u000e|\u000f'+\
                             u'|\u0010|\u0011|\u0012|\u0013|\u0014|\u0015|\u0016|\u0017|\u0018|\u0019|\u001a|\u001b|\u001c|\u001d|\u001e|\u001f)'
        mediainfo_xml_u = re.sub(invalid_char_match,char_repl,mediainfo_xml_u)

        invalid_dec_ref_match = '&#0*(0|1|2|3|4|5|6|7|8|11|12|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31);'
        mediainfo_xml_u = re.sub(invalid_dec_ref_match,dec_ref_repl,mediainfo_xml_u)

        invalid_hex_ref_match = '&#x0*(0|1|2|3|4|5|6|7|8|b|B|c|C|e|E|f|F|10|11|12|13|14|15|16|17|18|19|1a|1A|1b|1B|1c|1C|1d|1D|1e|1E|1f|1F);'
        mediainfo_xml_u = re.sub(invalid_hex_ref_match,hex_ref_repl,mediainfo_xml_u)


        # In Python 2.x, ElementTree.fromstring() only works if an str type is passed.
        # Most likely, the encoding of the str value needs to match the encoding stated
        # in the xml statement in the XML infoset (i.e. UTF-8).
        # The error handling method "replace" causes U+FFFD characters (unknown char)
        # to be replaced with "?".
        mediainfo_xml_str = mediainfo_xml_u.encode("utf-8","replace")

        try:
            root_elem = xml.etree.ElementTree.fromstring(mediainfo_xml_str)
            # Any element content and attribute values are unicode typed strings (definitely if needed, not sure whether always).
            rc = 0
        except xml.etree.ElementTree.ParseError as (err):
            utils.ErrorMsg("Missing media info: Cannot parse XML output of mediainfo_cli: "+str(err)+" for file: \""+moviefile_uncpath+"\"", num_errors)
            rc = -1

        if rc == 0:
            if root_elem == None:
                utils.ErrorMsg("Missing media info: mediainfo_cli did not produce XML output for file: \""+moviefile_uncpath+"\"", num_errors)
            else:
                track_elem_list = root_elem.findall("File/track")
                if track_elem_list == None:
                    utils.ErrorMsg("Missing media info: mediainfo_cli XML output does not have any <track> elements for file: \""+moviefile_uncpath+"\"", num_errors)
                else:
                    if len(track_elem_list) < 3:
                        # This symptom is caused by files that are being written as part of conversion.
                        utils.WarningMsg("Missing media info: mediainfo_cli XML output does not have the expected 3 or more <track> elements (possibly being written): \""+moviefile_uncpath+"\"")
                    else:
                        general_elem = None
                        video_elem = None
                        audio_elem = None
                        for elem in track_elem_list:
                            if elem.get("type") == "General":
                                general_elem = elem
                            if elem.get("type") == "Video":
                                video_elem = elem
                            if elem.get("type") == "Audio":
                                if audio_elem == None:
                                    # remember the first audio stream
                                    audio_elem = elem
                                else:
                                    # issue a warning for the second and further audio streams, for now.
                                    utils.WarningMsg("Ignoring additional audio stream in file: \""+moviefile_uncpath+"\"")

                        if general_elem == None:
                            utils.ErrorMsg("Missing media info: mediainfo_cli XML output does not have a <track> element of type 'General' for file: \""+moviefile_uncpath+"\"", num_errors)
                        else:

                            _elem = general_elem.find("Format")
                            if _elem != None:
                                movie["container_format"] = _elem.text
                                movie["idContainerFormat"] = GetIdContainerFormat(_elem.text, moviefile_uncpath)

                            _elem = general_elem.find("Movie_name")
                            if _elem != None:
                                title_tag = _elem.text

                                try:
                                    parsed_filename_tag = utils.ParseMovieFilename(title_tag,tolerate_noext=True)
                                except utils.ParseError as exc:
                                    utils.ErrorMsg(u"Missing media info: "+unicode(exc))
                                else:
                                    complex_title = parsed_filename_tag["complex_title"]
                                    try:
                                        parsed_complex_title_tag = utils.ParseComplexTitle(complex_title)
                                    except utils.ParseError as exc:
                                        utils.ErrorMsg(u"Missing media info: "+unicode(exc))
                                    else:
                                        movie["title"] = parsed_complex_title_tag["title"]
                                        movie["year"] = parsed_complex_title_tag["year"]
                                        movie["series_title"] = parsed_complex_title_tag["series_title"]
                                        movie["episode_title"] = parsed_complex_title_tag["episode_title"]
                                        movie["episode_id"] = parsed_complex_title_tag["episode_id"]
                            _elem = general_elem.find("Duration")
                            if _elem != None:
                                _v = _elem.text   # e.g. "1h 36mn" or "28mn 43s"
                                _v_list = _v.split(" ")
                                _d = 0
                                for _v2 in _v_list:
                                    if _v2.endswith("h"):
                                        _d += 60*int(_v2[0:_v2.find("h")])
                                    if _v2.endswith("mn"):
                                        _d += int(_v2[0:_v2.find("mn")])
                                    if _v2.endswith("s"):
                                        _d += 1 # seconds are replaced by one more minute
                                movie["duration_min"] = str(_d)

                        if video_elem == None:
                            utils.ErrorMsg("Missing media info: mediainfo_cli XML output does not have a <track> element of type 'Video' for file: \""+moviefile_uncpath+"\"", num_errors)
                        else:

                            _elem = video_elem.find("Format")
                            if elem != None:
                                movie["video_format"] = _elem.text
                                _format = _elem.text
                            else:
                                _format = None

                            _elem = video_elem.find("Format_profile")
                            if _elem != None:
                                movie["video_format_profile"] = _elem.text
                                _profile = _elem.text
                            else:
                                _profile = None

                            movie["idVideoFormat"] = GetIdVideoFormat(_format, _profile, moviefile_uncpath)

                            _elem = video_elem.find("Bit_rate")
                            if _elem != None:
                                _v = _elem.text   # e.g. "1 296 Kbps"
                                _v = _v.replace(" ","")
                                _v = _v[0:_v.find("bps")]
                                if _v.endswith("K"):
                                    _v = float(_v[0:len(_v)-1])*1
                                elif _v.endswith("M"):
                                    _v = float(_v[0:len(_v)-1])*1000
                                else:
                                    _v = float(_v)
                                movie["video_bitrate_kbps"] = str(_v)

                            _elem = video_elem.find("Width")
                            if _elem != None:
                                _v = _elem.text   # e.g. "1 280 pixels"
                                _v = _v.replace(" ","")
                                _v = int(_v[0:_v.find("pixels")])
                                movie["video_width"] = str(_v)

                            _elem = video_elem.find("Height")
                            if _elem != None:
                                _v = _elem.text   # e.g. "1 080 pixels"
                                _v = _v.replace(" ","")
                                _v = int(_v[0:_v.find("pixels")])
                                movie["video_height"] = str(_v)

                            _elem = video_elem.find("Display_aspect_ratio")
                            if _elem != None:
                                _v = _elem.text   # e.g. "16:9" or "1.25" or "16.0:9.0"
                                _colon = _v.find(":")
                                if _colon >= 0:
                                    # we assume there is a number before and after the colon
                                    _v = float(_v[0:_colon]) / float(_v[_colon+1:])
                                else:
                                    _v = float(_v)
                                movie["video_dar"] = str(_v)

                            _elem = video_elem.find("Original_display_aspect_ratio")
                            if _elem != None:
                                _v = _elem.text   # e.g. "16:9" or "1.25" or "16.0:9.0"
                                _colon = _v.find(":")
                                if _colon >= 0:
                                    # we assume there is a number before and after the colon
                                    _v = float(_v[0:_colon]) / float(_v[_colon+1:])
                                else:
                                    _v = float(_v)
                                movie["video_dar_org"] = str(_v)

                            _elem = video_elem.find("Frame_rate")
                            if _elem != None:
                                _v = _elem.text   # e.g. "25.000 fps"
                                _v = _v.replace(" ","")
                                _v = float(_v[0:_v.find("fps")])
                                movie["video_framerate_fps"] = str(_v)

                            _elem = video_elem.find("Frame_rate_mode")
                            if _elem != None:
                                movie["video_framerate_mode"] = _elem.text
                                movie["idVideoFramerateMode"] = GetIdVideoFramerateMode(_elem.text, moviefile_uncpath)

                        if audio_elem == None:
                            utils.ErrorMsg("Missing media info: mediainfo_cli XML output does not have a <track> element of type 'Audio' for file: \""+moviefile_uncpath+"\"", num_errors)
                        else:

                            _elem = audio_elem.find("Format")
                            if elem != None:
                                movie["audio_format"] = _elem.text
                                _format = _elem.text
                            else:
                                _format = None

                            _elem = audio_elem.find("Format_profile")
                            if _elem != None:
                                movie["audio_format_profile"] = _elem.text
                                _profile = _elem.text
                            else:
                                _profile = None

                            movie["idAudioFormat"] = GetIdAudioFormat(_format, _profile, moviefile_uncpath)

                            _elem = audio_elem.find("Bit_rate")
                            if _elem != None:
                                _v = _elem.text  # e.g. "152 Kbps"
                                _v = _v.replace(" ","")
                                _v = _v[0:_v.find("bps")]
                                if _v.endswith("K"):
                                    _v = float(_v[0:len(_v)-1])*1
                                elif _v.endswith("M"):
                                    _v = float(_v[0:len(_v)-1])*1000
                                else:
                                    _v = float(_v)
                                movie["audio_bitrate_kbps"] = str(_v)

                            _elem = audio_elem.find("Bit_rate_mode")
                            if _elem != None:
                                movie["audio_bitrate_mode"] = _elem.text
                                movie["idAudioBitrateMode"] = GetIdAudioBitrateMode(_elem.text, moviefile_uncpath)

                            _elem = audio_elem.find("Sampling_rate")
                            if _elem != None:
                                _v = _elem.text  # e.g. "44.1 KHz"
                                _v = _v.replace(" ","")
                                _v = _v[0:_v.find("Hz")]
                                if _v.endswith("K"):
                                    _v = float(_v[0:len(_v)-1])*1000
                                else:
                                    _v = float(_v)
                                movie["audio_samplingrate_hz"] = str(_v)


    return movie


#------------------------------------------------------------------------------
def UpdateFile(moviefile_uncpath):
    """Update information about a movie file in the movie database.

    Parameters:
        moviefile_uncpath:  UNC file path of the movie file (with Windows separators, as unicode types)
    """

    global num_errors, verbose_mode

    utils.Msg("Updating file: \""+moviefile_uncpath+"\" ...", verbose_mode)

    movie = GetMovieInfo(moviefile_uncpath)
    if movie == None:
        return

    cv = ""          # column=value list for UPDATE
    cv += "idMovie = NULL, "
    cv += "idMediumType = 'FILE', "
    cv += "idStatus = %(status)s, "
    cv += "Uncut = %(fn_uncut)s, "
    cv += "Language = %(fn_language)s, "
    cv += "SubtitleLanguage = %(fn_subtitle_language)s, "
    cv += "Duration = %(duration_min)s, "
    cv += "idQuality = %(idVideoQuality)s, "
    cv += "DesiredDisplayAspectRatioWidth = %(fn_dar_width)s, "
    cv += "DesiredDisplayAspectRatioHeight = %(fn_dar_height)s, "
    cv += "DisplayAspectRatio = %(video_dar)s, "
    cv += "OriginalDisplayAspectRatio = %(video_dar_org)s, "
    cv += "idContainerFormat = %(idContainerFormat)s, "
    cv += "idVideoFormat = %(idVideoFormat)s, "
    cv += "VideoFormatProfile = %(video_format_profile)s, "
    cv += "VideoSamplingWidth = %(video_width)s, "
    cv += "VideoSamplingHeight = %(video_height)s, "
    cv += "VideoBitrate = %(video_bitrate_kbps)s, "
    cv += "VideoFramerate = %(video_framerate_fps)s, "
    cv += "idVideoFramerateMode = %(idVideoFramerateMode)s, "
    # cv += "VideoQualityFactor = '', "         # TBD: Get this value from MediaInfo
    cv += "idAudioFormat = %(idAudioFormat)s, "
    cv += "AudioFormatProfile = %(audio_format_profile)s, "
    # cv += "idAudioChannelType = '', "         # TBD: Get this value from MediaInfo
    cv += "TechnicalFlaws = %(fn_techcomm)s, "
    cv += "AudioBitrate = %(audio_bitrate_kbps)s, "
    cv += "idAudioBitrateMode = %(idAudioBitrateMode)s, "
    cv += "AudioSamplingRate = %(audio_samplingrate_hz)s, "
    now = str(datetime.datetime.now())[0:19]
    cv += "TSUpdated = '"+now+"', "
    cv += "TSVerified = '"+now+"', "
    cv += "Title = %(title)s, "
    cv += "ReleaseYear = %(year)s, "
    cv += "SeriesTitle = %(series_title)s, "
    cv += "EpisodeTitle = %(episode_title)s, "
    cv += "EpisodeId = %(episode_id)s, "
    cv += "FolderPath = %(folder_path)s"

    # movie["fn_threed"]+", "
    # movie["fn_partial"]+", "

    sql = "UPDATE Medium SET "+cv+" WHERE FilePath = %(file_path)s AND idCabinet = %(idCabinet)s"

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)

    medium_cursor.execute(sql,movie)

    medium_cursor.close()

    movies_conn.commit()

#------------------------------------------------------------------------------
def AddFile(moviefile_uncpath):
    """Add information about a movie file to the movie database.

    Parameters:
        moviefile_uncpath:  UNC file path of the movie file (with Windows separators, as unicode types)
    """

    global num_errors, verbose_mode
    global movies_conn

    utils.Msg("Adding file: \""+moviefile_uncpath+"\" ...", verbose_mode)

    movie = GetMovieInfo(moviefile_uncpath)
    if movie == None:
        return

    c = ""          # column list for INSERT
    v = ""          # value list for INSERT
    c += "idMovie, "
    v += "NULL, "
    c += "idCabinet, "
    v += "%(idCabinet)s, "
    c += "idMediumType, "
    v += "'FILE', "
    c += "idStatus, "
    v += "%(status)s, "
    c += "Uncut, "
    v += "%(fn_uncut)s, "
    c += "Language, "
    v += "%(fn_language)s, "
    c += "SubtitleLanguage, "
    v += "%(fn_subtitle_language)s, "
    c += "Duration, "
    v += "%(duration_min)s, "
    c += "idQuality, "
    v += "%(idVideoQuality)s, "
    c += "DesiredDisplayAspectRatioWidth, "
    v += "%(fn_dar_width)s, "
    c += "DesiredDisplayAspectRatioHeight, "
    v += "%(fn_dar_height)s, "
    c += "DisplayAspectRatio, "
    v += "%(video_dar)s, "
    c += "OriginalDisplayAspectRatio, "
    v += "%(video_dar_org)s, "
    c += "idContainerFormat, "
    v += "%(idContainerFormat)s, "
    c += "idVideoFormat, "
    v += "%(idVideoFormat)s, "
    c += "VideoFormatProfile, "
    v += "%(video_format_profile)s, "
    c += "VideoSamplingWidth, "
    v += "%(video_width)s, "
    c += "VideoSamplingHeight, "
    v += "%(video_height)s, "
    c += "VideoBitrate, "
    v += "%(video_bitrate_kbps)s, "
    c += "VideoFramerate, "
    v += "%(video_framerate_fps)s, "
    c += "idVideoFramerateMode, "
    v += "%(idVideoFramerateMode)s, "
    # c += "VideoQualityFactor, "
    # v +=                                    # TBD: Get this value from MediaInfo
    c += "idAudioFormat, "
    v += "%(idAudioFormat)s, "
    c += "AudioFormatProfile, "
    v += "%(audio_format_profile)s, "
    # c += "idAudioChannelType, "
    # v +=                                    # TBD: Get this value from MediaInfo
    c += "TechnicalFlaws, "
    v += "%(fn_techcomm)s, "
    c += "AudioBitrate, "
    v += "%(audio_bitrate_kbps)s, "
    c += "idAudioBitrateMode, "
    v += "%(idAudioBitrateMode)s, "
    c += "AudioSamplingRate, "
    v += "%(audio_samplingrate_hz)s, "
    c += "FilePath, "
    v += "%(file_path)s, "
    c += "FolderPath, "
    v += "%(folder_path)s, "
    now = str(datetime.datetime.now())[0:19]
    c += "TSUpdated, "
    v += "'"+now+"', "
    c += "TSVerified, "
    v += "'"+now+"', "
    c += "Title, "
    v += "%(title)s, "
    c += "ReleaseYear, "
    v += "%(year)s, "
    c += "SeriesTitle, "
    v += "%(series_title)s, "
    c += "EpisodeTitle, "
    v += "%(episode_title)s, "
    c += "EpisodeId"
    v += "%(episode_id)s"

    # movie["fn_threed"]+", "
    # movie["fn_partial"]+", "

    sql = "INSERT INTO Medium ("+c+") VALUES ( "+v+")"

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)

    medium_cursor.execute(sql,movie)

    medium_cursor.close()

    movies_conn.commit()


#------------------------------------------------------------------------------
def RemoveFile(moviefile_uncpath):
    """Remove information about a movie file from the movie database.

    Parameters:
        moviefile_uncpath:  UNC file path of the movie file (with Windows separators, as unicode types)
    """

    global num_errors, verbose_mode
    global movies_conn

    utils.Msg("Removing file: \""+moviefile_uncpath+"\" ...", verbose_mode)

    # Split file path into UNC resource name and local file path
    _spos = moviefile_uncpath.find("\\",2)         # 0-based position of first backslash after initial "\\" (i.e. between server and share name)
    _ppos = moviefile_uncpath.find("\\",_spos+1)   # 0-based position of backslash that separates UNC resource name and local file path
    if moviefile_uncpath[0:2] == "\\\\" and _spos > 0 and _ppos > 0:
        res = moviefile_uncpath[0:_ppos]        # UNC resource name (e.g. \\192.168.0.12\share)
        path = moviefile_uncpath[_ppos:]        # local file path on the UNC resource, with leading backslash
    else:
        utils.ErrorMsg("File path does not start with UNC resource name: "+moviefile_uncpath, num_errors)
        res = None
        path = None


    movie = dict()
    movie["idCabinet"] = str(GetIdCabinet(res, moviefile_uncpath))
    movie["_filepath"] = path

    sql = "DELETE FROM Medium WHERE idCabinet = %(idCabinet)s AND FilePath = %(_filepath)s"

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)

    medium_cursor.execute(sql,movie)

    medium_cursor.close()

    movies_conn.commit()


#------------------------------------------------------------------------------
def GetIdVideoQuality(name, moviefile_uncpath):

    global idvideoquality_dict
    global num_errors, verbose_mode

    if name == None:
        _id = None
        utils.ErrorMsg("Missing media info: No video quality in filename of movie file: "+moviefile_uncpath, num_errors)
    else:
        if name in idvideoquality_dict:
            _id = idvideoquality_dict[name]
        else:
            _id = None
            utils.ErrorMsg("Missing media info: Unknown video quality '"+name+"' in filename of movie file: "+moviefile_uncpath, num_errors)

    return _id

#------------------------------------------------------------------------------
def GetIdContainerFormat(field_value, moviefile_uncpath):

    global idcontainerformat_dict
    global num_errors, verbose_mode

    if field_value in idcontainerformat_dict:
        _id = idcontainerformat_dict[field_value]
    else:
        _id = None
        utils.ErrorMsg("Missing media info: Unknown container format field value '"+str(field_value)+"' in movie file: "+moviefile_uncpath, num_errors)

    return _id

#------------------------------------------------------------------------------
def GetIdVideoFormat(format_field_value, profile_field_value, moviefile_uncpath):

    global fixedvideoformat_list
    global num_errors, verbose_mode

    _id = None
    for _row in fixedvideoformat_list:
        if _row["FormatFieldValue"] == format_field_value:
            if _row["ProfileFieldValue"] == profile_field_value:
                _id = _row["idVideoFormat"]
                break
            elif _row["ProfileFieldValue"] == None:
                _id = _row["idVideoFormat"]
                break

    if _id == None:
        utils.ErrorMsg("Missing media info: Unknown video format field value '"+str(format_field_value)+"' or profile field value '"+str(profile_field_value)+"' in movie file: "+moviefile_uncpath, num_errors)

    return _id

#------------------------------------------------------------------------------
def GetIdAudioFormat(format_field_value, profile_field_value, moviefile_uncpath):

    global fixedaudioformat_list
    global num_errors, verbose_mode

    _id = None
    for _row in fixedaudioformat_list:
        if _row["FormatFieldValue"] == format_field_value:
            if _row["ProfileFieldValue"] == profile_field_value:
                _id = _row["idAudioFormat"]
                break
            elif _row["ProfileFieldValue"] == None:
                _id = _row["idAudioFormat"]
                break

    if _id == None:
        utils.ErrorMsg("Missing media info: Unknown audio format field value '"+str(format_field_value)+"' or profile field value '"+str(profile_field_value)+"' in movie file: "+moviefile_uncpath, num_errors)

    return _id

#------------------------------------------------------------------------------
def GetIdVideoFramerateMode(field_value, moviefile_uncpath):

    global idvideoframeratemode_dict
    global num_errors, verbose_mode

    if field_value in idvideoframeratemode_dict:
        _id = idvideoframeratemode_dict[field_value]
    else:
        _id = None
        utils.ErrorMsg("Missing media info: Unknown video framerate mode field value '"+str(field_value)+"' in movie file: "+moviefile_uncpath, num_errors)

    return _id

#------------------------------------------------------------------------------
def GetIdAudioBitrateMode(field_value, moviefile_uncpath):

    global idaudiobitratemode_dict
    global num_errors, verbose_mode

    if field_value in idaudiobitratemode_dict:
        _id = idaudiobitratemode_dict[field_value]
    else:
        _id = None
        utils.ErrorMsg("Missing media info: Unknown audio bitrate mode field value '"+str(field_value)+"' in movie file: "+moviefile_uncpath, num_errors)

    return _id

#------------------------------------------------------------------------------
def GetIdCabinet(smb_server_resource, moviefile_uncpath):

    global idcabinet_dict
    global num_errors, verbose_mode

    if smb_server_resource in idcabinet_dict:
        _id = idcabinet_dict[smb_server_resource]
    else:
        _id = None
        utils.ErrorMsg("Missing media info: Media cabinet for SMB server resource '"+str(smb_server_resource)+"' not found in movie database, file: "+moviefile_uncpath, num_errors)

    return _id


#------------------------------------------------------------------------------
# main routine
#


my_name = os.path.basename(os.path.splitext(sys.argv[0])[0])

utils.Msg( my_name+" Version "+version.__version__)


num_errors = 0                  # number of errors
verbose_mode = False            # verbose mode, controlled by -v option
update_all = False              # update all movies instead of outdated, controlled by -a option

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


# Build information about source files, by scanning source locations.

utils.Msg("Scanning source locations for movie files...")

sourcepath_list = list() # list of source files (in addition to dict, to maintain order)

sourcepath_dict = dict()
# dictionary of source files
# key: UNC file path (with Windows separators, as unicode types)
# value: object:
#   "status": status value, see config.FILE_SOURCES["status"] for description
#   "folder_path": display folder path, for FolderPath column.

for file_source in config.FILE_SOURCES:

    source_res_w = file_source["res"]
    if type(source_res_w) == str:
        source_res_w = source_res_w.decode()

    source_dir_w = file_source["dir"]
    if type(source_dir_w) == str:
        source_dir_w = source_dir_w.decode()

    source_folder_root_w = file_source["folder_root"]
    if type(source_folder_root_w) == str:
        source_folder_root_w = source_folder_root_w.decode()
    if not source_folder_root_w.endswith("\\"):
        source_folder_root_w += "\\"

    source_patterns = file_source["patterns"]
    if type(source_patterns) == str:
        source_patterns = source_patterns.decode()

    source_status = file_source["status"]

    source_path_w = source_res_w + source_dir_w

    utils.Msg(u"Source location: \""+source_path_w+"\" ...", verbose_mode)

    files = list()
    for pattern in source_patterns:
        # RecursiveGlob returns filenames in unicode, if directory parameter is in unicode.
        files += utils.RecursiveGlob(source_path_w, pattern)
    files = sorted(files)

    for _file in files:
        folder_path = source_folder_root_w + os.path.relpath(os.path.dirname(_file),source_path_w)
        folder_path = folder_path.replace("\\","/").rstrip("/.")
        sourcepath_list.append(_file)
        sourcepath_dict[_file] = { "status": source_status, "folder_path": folder_path }

utils.Msg("Found "+str(len(sourcepath_list))+" movie files in source locations")


# Connection to movie database
movies_conn = MySQLdb.connect( host=config.MYSQL_HOST, user=config.MYSQL_USER,
                               db=config.MYSQL_DB, use_unicode=True, charset='utf8')
# Todo: exception handling, e.g. _mysql_exceptions.OperationalError

# Build idvideoquality_dict dictionary from FixedQuality table in movie database
_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute("SELECT idVideoQuality,Name FROM FixedQuality")
_rows = _cursor.fetchall()
_cursor.close()
idvideoquality_dict = dict()    # dictionary for translating quality names into idVideoQuality key values
                                # key: quality name (FixedQuality.Name), e.g. "HD", "HD+SD", "HQ-low", ...
                                # value: idVideoQuality key value (for FixedQuality table)
for _row in _rows:
    idvideoquality_dict[_row["Name"]] = _row["idVideoQuality"]


# Build idcontainerformat_dict dictionary from FixedContainerFormat table in movie database
_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute("SELECT idContainerFormat,FieldValue FROM FixedContainerFormat")
_rows = _cursor.fetchall()
_cursor.close()
idcontainerformat_dict = dict() # dictionary for translating container format field values into idContainerFormat key values
                                # key: container format field value (FixedContainerFormat.FieldValue)
                                # value: idContainerFormat key value (for FixedContainerFormat table)
for _row in _rows:
    idcontainerformat_dict[_row["FieldValue"]] = _row["idContainerFormat"]


# Build idvideoformat_dict dictionary from FixedVideoFormat table in movie database
_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute("SELECT idVideoFormat,FormatFieldValue,ProfileFieldValue FROM FixedVideoFormat ORDER BY idVideoFormat")
_rows = _cursor.fetchall()
_cursor.close()
fixedvideoformat_list = _rows   # array that is a copy of table FixedVideoFormat. Each row is an array entry that is
                                # an object with properties for the following columns of that table:
                                #   idVideoFormat, FormatFieldValue, ProfileFieldValue.


# Build idaudioformat_dict dictionary from FixedAudioFormat table in movie database
_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute("SELECT idAudioFormat,FormatFieldValue,ProfileFieldValue FROM FixedAudioFormat ORDER BY idAudioFormat")
_rows = _cursor.fetchall()
_cursor.close()
fixedaudioformat_list = _rows   # array that is a copy of table FixedAudioFormat. Each row is an array entry that is
                                # an object with properties for the following columns of that table:
                                #   idAudioFormat, FormatFieldValue, ProfileFieldValue.


# Build idvideoframeratemode_dict dictionary from FixedVideoFramerateMode table in movie database
_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute("SELECT idVideoFramerateMode,FieldValue FROM FixedVideoFramerateMode")
_rows = _cursor.fetchall()
_cursor.close()
idvideoframeratemode_dict = dict() # dictionary for translating video framerate mode field values into idVideoFramerateMode key values
                                # key: video framerate mode field value (FixedVideoFramerateMode.FieldValue)
                                # value: idVideoFramerateMode key value (for FixedVideoFramerateMode table)
for _row in _rows:
    idvideoframeratemode_dict[_row["FieldValue"]] = _row["idVideoFramerateMode"]


# Build idaudiobitratemode_dict dictionary from FixedAudioBitrateMode table in movie database
_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute("SELECT idAudioBitrateMode,FieldValue FROM FixedAudioBitrateMode")
_rows = _cursor.fetchall()
_cursor.close()
idaudiobitratemode_dict = dict() # dictionary for translating audio bitrate mode field values into idAudioBitrateMode key values
                                # key: audio bitrate mode field value (FixedAudioBitrateMode.FieldValue)
                                # value: idAudioBitrateMode key value (for FixedAudioBitrateMode table)
for _row in _rows:
    idaudiobitratemode_dict[_row["FieldValue"]] = _row["idAudioBitrateMode"]


# Get all SMB file cabinets known in movie database and build cabinet_dict
cabinet_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
cabinet_cursor.execute("SELECT * FROM Cabinet WHERE idCabinetType = 'SMB'")
cabinet_rows = cabinet_cursor.fetchall()
cabinet_cursor.close()
cabinet_dict = dict()   # dictionary of SMB file cabinets in movie database
                        # key: cabinet id
                        # value: UNC name of SMB resource share
idcabinet_dict = dict() # dictionary of SMB file cabinets in movie database
                        # key: UNC name of SMB resource share
                        # value: cabinet id
for cabinet_row in cabinet_rows:
    res = "\\\\"+cabinet_row["SMBServerHost"]+"\\"+cabinet_row["SMBServerShare"]
    cabinet_id = cabinet_row["idCabinet"]
    cabinet_dict[cabinet_id] = res
    idcabinet_dict[res] = cabinet_id


# Get all movie files known in movie database, and build mediumpath_dict
medium_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
medium_cursor.execute("SELECT FilePath,TSUpdated,TSVerified,idCabinet FROM Medium WHERE idMediumType = 'FILE'")

mediumpath_dict = dict()
# dictionary of medium files in movie database
# key: UNC file path (with Windows separators, as unicode types)
# value: object:
#   "updated": date where medium row was last updated
#   "verified": date where file existence was last verified

while True:
    medium_row = medium_cursor.fetchone()
    if medium_row == None:
        break
    idCabinet = medium_row["idCabinet"]
    resource_uncpath = cabinet_dict[idCabinet]
    if type(resource_uncpath) == str:
        resource_uncpath = resource_uncpath.decode()
    obj = { "updated": medium_row["TSUpdated"], "verified": medium_row["TSVerified"] }
    relpath = medium_row["FilePath"]
    if type(relpath) == str:
        relpath = relpath.decode()
    mediumpath = resource_uncpath + relpath
    mediumpath_dict[mediumpath] = obj
medium_cursor.close()

# Release all read locks
movies_conn.commit()

utils.Msg("Found "+str(len(mediumpath_dict))+" movie files in movie database")


utils.Msg("Updating movie database from source locations...")

for sourcepath in sourcepath_list:

    try:
        file_modified_dt = datetime.datetime.fromtimestamp(os.stat(sourcepath).st_mtime)
        file_no_longer_exists = False
    except:
        file_modified_dt = None
        file_no_longer_exists = True

    if file_no_longer_exists:

        utils.WarningMsg(u"Skipping movie file that was deleted since scanning source location: \""+sourcepath+"\" ...")

    else:

        basefile = os.path.basename(sourcepath)
        m = re.match(r"^.+\(.*(FHD|HD|HQ|SD)(\+(HD|HQ|SD))?(-low)? [0-9]+x[0-9]+.*\)\..+$",basefile)
        if m == None:

            utils.WarningMsg(u"Skipping movie file with unknown file name format: \""+sourcepath+"\" ...")

        else:

            if sourcepath in mediumpath_dict:
                medium_updated_dt = mediumpath_dict[sourcepath]["updated"] # datetime type
                if file_modified_dt > medium_updated_dt or update_all:
                    UpdateFile(sourcepath)
                else:
                    pass # Skip unchanged movie file
            else:
                AddFile(sourcepath)

for mediumpath in mediumpath_dict:
    if mediumpath not in sourcepath_list:
        RemoveFile(mediumpath)


if num_errors > 0:
    utils.ErrorMsg("Finished with "+str(num_errors)+" errors.")
    exit(12)
else:
    utils.Msg("Success.")
    exit(0)
