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
# Change log:
#   V1.0.3 2012-06-24
#     Added support for MediaInfo 0.7.58, by changing --output=xml to --output=XML
#     Added U+00AA and U+0152 to xmlrep_trans translation list to fix issue with invalid XML produced by MediaInfo.

my_name = "movies_updatemedia"
my_version = "1.0.4"

import re, sys, glob, os, os.path, string, errno, locale, fnmatch, subprocess, xml.etree.ElementTree, datetime
from operator import itemgetter, attrgetter, methodcaller
import MySQLdb
from movies_conf import *


std_patterns = [ "*.mp4", "*.avi" ]             # standard file patterns to search for

# file sources to be processed

file_sources = [
    {
      "res":      fileserver_share,             # UNC name of resource on file server
      "dir":      "\\admauto",                  # directory path of subtree on that resource
      "patterns": std_patterns,                 # file patterns in subtree to be used
      "status":   "WORK"                        # status of this subtree (using values of idStatus column in FixedStatus table)
    },
    {
      "res":      fileserver_share,
      "dir":      "\\Movies\\MissingParts",
      "patterns": std_patterns,
      "status":   "MISSINGPARTS"
    },
    {
      "res":      fileserver_share,
      "dir":      "\\Movies\\LowResolution+Duplicates",
      "patterns": std_patterns,
      "status":   "DUPLICATE"
    },
    {
      "res":      fileserver_share,
      "dir":      "\\Movies\\share",
      "patterns": std_patterns,
      "status":   "SHARED"
    },
    {
      "res":      fileserver_share,
      "dir":      "\\Movies\\share.disabled",
      "patterns": std_patterns,
      "status":   "DISABLED"
    },
]

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
    print "Updates movie file data in a MySQL server from movie files on a file server."
    print ""
    print "Usage:"
    print "  "+my_name+" [options]"
    print ""
    print "Options:"
    print "  -a          Update all movies, instead of just those whose records are outdated."
    print "  -v          Verbose mode: Display additional messages."
    print "  -t          Test mode: Go only through test subtree."
    print ""
    print "MySQL server:"
    print "  host: "+mysql_host+" (default port 3306)"
    print "  user: "+mysql_user+" (no password)"
    print "  database: "+mysql_db
    print ""
    print "Locations of movie files:"
    for file_source in file_sources:
        print "  "+file_source["res"]+file_source["dir"]
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

    global num_errors

    print >>sys.stderr, "Error: "+msg
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

    global quiet_mode

    if quiet_mode == False:
        print msg
        sys.stdout.flush()

    return

#------------------------------------------------------------------------------
def runCmd(cmd, timeout=None):
    """
    Execute a command under timeout control and return its standard output, standard error and exit code
    @param cmd: Command to execute
    @param timeout: Timeout in seconds
    @return: Tuple: stdout string, stderr string, exit code (int)
    @raise OSError: on missing command or if a timeout was reached
    """

    stdout_str = None   # stdout string of command
    stderr_str = None   # stderr string of command
    exit_code = None    # exit code of command

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
            raise OSError("Process timeout has been reached")

        exit_code = p.returncode

    stdout_str, stderr_str = p.communicate()

    return stdout_str, stderr_str, exit_code


#------------------------------------------------------------------------------
def rglob(directory, fnpattern):
    filenames = []
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, fnpattern):
                filenames.append(os.path.join(root, basename))
    return filenames


#------------------------------------------------------------------------------
def GetMovieInfo(file_w):
    # file_w: UNC resource name and file path of the movie file, in CP1250 (Windows file system) and with backslashes.

    global xmlrep_trans
    
    ufile_w = unicode(file_w.decode("cp1250")) # file names on Windows are returned to Python in cp1250.

    ubasefile_w = os.path.basename(ufile_w)

    # Split file path into UNC resource name and local file path
    _spos = ufile_w.find("\\",2)         # 0-based position of first backslash after initial "\\" (i.e. between server and share name)
    _ppos = ufile_w.find("\\",_spos+1)   # 0-based position of backslash that separates UNC resource name and local file path
    if ufile_w[0:2] == "\\\\" and _spos > 0 and _ppos > 0:
        ures_w = ufile_w[0:_ppos]        # UNC resource name (e.g. \\192.168.0.12\share)
        upath_w = ufile_w[_ppos:]        # local file path on the UNC resource, with leading backslash
    else:
        ErrorMsg("File path does not start with UNC resource name: "+ufile_w)
        ures_w = None
        upath_w = None


    # basefile format:
    #  {title} [({year}) ]([3D ][{lang} ]{q} {dar}[ {techcomm}])[.{techcomm2}][.{dup}][.uncut].{ext}
    # Where:
    #  The use of [] indicates optional elements, () are used as literals.
    #  {title} = Title of the movie, sometimes with eposide number, etc. May contain additional parenthesis.
    #  {year} = Release year of the movie, may appear at the indicated position or within {title}
    #  Quality block:
    #    3D = Indicates that the movie is some sort of 3D movie
    #    {lang} = Language of the audio in the movie and of any subtitles: en, fr-U, ar-U-fr, etc.
    #             The -U says the movie has subtitles (Untertitel).
    #             The default language is "de", both of the audio stream and of the subtitles.
    #             It is not currently supported to have more than one audio stream per media file (e.g. for different
    #             languages).
    #    {q} = quality: HD, HQ, SD, HQ-low, HD+SD, etc.
    #    {dar} = Display Aspect Ratio: 16x9, 4x3, etc.
    #    {techkomm} = technical comments of final movie, e.g. "size varies"
    #  {techkomm2} = technical comments of non-final movie, e.g. "missing-end"
    #  {dup} = Duplicate indicator, a number to distinguish duplicates, usually starting with 2.
    #  .uncut = Indicates that the movie is not yet cut (i.e. contains advertisements, or extra content at begin or end)
    #  .{ext} = File extension, indicates the container format: .mp4, .divx.avi, .mpg.avi

    pdot = ubasefile_w.rfind(").")    # last ").", expected to be closing paren. of quality block

    if pdot == -1:
        status = "INVALIDFN"
        title = None
        year = None
        uncut = None
        format = None
        threed = None
        language = None
        subtitle_language = None
        quality = None
        dar_w = None
        dar_h = None
        techcomm = None
        partial = None

    else:

        bf1 = ubasefile_w[0:pdot+1]     # from begin up to and including last ")"
        bf2 = ubasefile_w[pdot+1:]      # from next char after last ")" to end (including file extension)

        qblock_paren_pos = bf1.rfind("(")  # position of "(qblock)" (= quality block)

        if qblock_paren_pos == -1:

            # "(qblock)" is required

            status = "INVALIDFN"
            title = None
            year = None
            uncut = None
            format = None
            threed = None
            language = None
            subtitle_language = None
            quality = None
            dar_w = None
            dar_h = None
            techcomm = None
            partial = None

        else:

            bf1a = bf1[0:qblock_paren_pos].strip(" ")   # bf1, without (qblock)

            # detect year in title
            m = re.match("(.*)\(([0-9]{4})\)(.*)",bf1a)
            if m != None:
                # bf1a contains a year "(nnnn)"
                # Msg("Debug: title contains year: _t1, year, _t2 = "+repr(m.groups()))
                _t1, year, _t2 = m.groups()
                title = _t1 + _t2
                title = title.replace("  "," ").replace(" , ",", ").strip(" ")
            else:
                year = None
                title = bf1a
                # Msg("Debug: title does not contain year")

            if bf2.find(".uncut.") >= 0:
                uncut = "1"
            else:
                uncut = "0"

            if bf2.find(".missing-end.") >= 0:
                partial = "missing-end"
            elif bf2.find(".just-end.") >= 0:
                partial = "just-end"
            elif bf2.find(".missing-begin.") >= 0:
                partial = "missing-begin"
            elif bf2.find(".just-begin.") >= 0:
                partial = "just-begin"
            else:
                partial = None

            if bf2.endswith(".mp4"):
                format = "MP4"
            elif bf2.endswith(".divx.avi"):
                format = "DIVX AVI"
            elif bf2.endswith(".mpg.avi"):
                format = "MPG AVI"
            else:
                format = "unknown"

            qblock = bf1[qblock_paren_pos+1:len(bf1)-1]+"  " # quality block, without ()
            word1, rest = qblock.split(" ",1)
            if word1 == "3D":
                threed = "3D"
                qblock = rest
            else:
                threed = None
            word1, rest = qblock.split(" ",1)

            # Language indicator (including subtitles)
            m = re.match("([a-z]{2,3})(-U(?:-([a-z]{2,3}))?)?",word1)
            if m != None:
                language = m.group(1) # audio language
                _gl = len(m.groups())
                if _gl == 1: # just the audio language specified, no -U
                    subtitle_language = None # No subtitles
                elif _gl == 2: # -U specified without subtitle language
                    subtitle_language = "de" # The default
                else: # -U specified with subtitle language
                    subtitle_language = m.group(2)
                qblock = rest
            else:
                language = "de" # The default
                subtitle_language = None # No subtitles

            quality, dar, techcomm = qblock.split(" ",2)
            techcomm = techcomm.strip(" ")
            quality = quality.strip(" ")
            dar = dar.strip(" ")
            dar_w, dar_h = dar.split("x")

            status = sourcepath_dict[file_w]["status"]

    movie = dict()
    movie["fn_title"] = title
    movie["title"] = title    # default, may be updated lateron by title tag
    movie["fn_year"] = year
    movie["status"] = status
    movie["fn_uncut"] = uncut
    movie["fn_container_format"] = format
    movie["fn_threed"] = threed
    movie["fn_language"] = language
    movie["fn_subtitle_language"] = subtitle_language
    movie["fn_quality"] = quality
    movie["idVideoQuality"] = GetIdVideoQuality(quality, ufile_w)
    movie["fn_dar_width"] = dar_w
    movie["fn_dar_height"] = dar_h
    movie["fn_techcomm"] = techcomm
    movie["fn_partial"] = partial
    movie["file_res"] = ures_w
    movie["file_path"] = upath_w
    movie["idCabinet"] = GetIdCabinet(ures_w, ufile_w)


    # Invoke MediaInfo on the file

    # The following timeout checking onlyworks on UNIX/Linux so far
    #
    # import signal
    #
    # # signal handler for mediainfo timeout alarm
    # def mediainfo_timeout_handler(signum, frame):
    #     print "Error: mediainfo_cli timeout (signal:"+signum+")."
    #
    # # Set the signal handler and a 30-second alarm
    # signal.signal(signal.SIGALRM, mediainfo_timeout_handler)
    # signal.alarm(30)

    start_time = datetime.datetime.now()

    try:
        child_process = subprocess.Popen(["mediainfo_cli", "--output=XML", file], stdout=subprocess.PIPE)
        # starts the process to run concurrently and returns

        mediainfo_xml = child_process.communicate()[0]
        # waits for child process to finish, and returns pipe output (encoded in UTF-8).

        rc = 0

    except OSError as (errno, strerror):

        ErrorMsg("Cannot call mediainfo_cli: "+strerror)
        rc = -1

    end_time = datetime.datetime.now()
    mediainfo_duration = (end_time - start_time).total_seconds()

    if mediainfo_duration > 10:
        Msg("Warning: Large mediainfo_cli execution time of "+str(round(mediainfo_duration))+" s for file: \""+file+"\"")

    # signal.alarm(0)          # Disable the alarm

    movie["title_tag"] = None
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

        #print "Debug: As produced by MediaInfo: mediainfo_xml="+repr(mediainfo_xml)

        # decode UTF-8 representation to Unicode characters.
        # "replace" means: Replace invalid UTF-8 characters with U+FFFD (Unicode character for invalid char)
        mediainfo_xml = mediainfo_xml.decode("utf-8","replace")

        # replace trouble characters that occur directly
        mediainfo_xml = mediainfo_xml.translate(xmlrep_trans)

        # replace invalid numeric character references (00..1F except 09 0D 0A).
        mediainfo_xml = re.sub(r'&#0*(0|1|2|3|4|5|6|7|8|11|12|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31);',r'Ud+\1',mediainfo_xml)
        mediainfo_xml = re.sub(r'&#x0*(0|1|2|3|4|5|6|7|8|0b|0c|0e|0f|10|11|12|13|14|15|16|17|18|19|1A|1B|1C|1D|1E|1F);',r'U+\1',mediainfo_xml)

        #print "Debug: After translation: mediainfo_xml="+repr(mediainfo_xml)
        #sys.stdout.flush()

        # encode Unicode characters to UTF-8 representation, replacing U+FFFD with "?"
        mediainfo_xml = mediainfo_xml.encode("utf-8","replace")

        try:
            root_elem = xml.etree.ElementTree.fromstring(mediainfo_xml)
            # This XML parser by default uses the encoding declared in the xml statement in the XML data (i.e. UTF-8)
            rc = 0
        except xml.etree.ElementTree.ParseError as (err):
            ErrorMsg("Cannot parse XML output of mediainfo_cli: "+str(err)+" for file: \""+file+"\"")
            rc = -1

        if rc == 0:
            if root_elem == None:
                ErrorMsg("mediainfo_cli did not produce XML output for file: \""+file+"\"")
            else:
                track_elem_list = root_elem.findall("File/track")
                if track_elem_list == None:
                    ErrorMsg("mediainfo_cli XML output does not have any <track> elements for file: \""+file+"\"")
                else:
                    if len(track_elem_list) != 3:
                        ErrorMsg("mediainfo_cli XML output does not have the expected 3 <track> elements for file: \""+file+"\"")
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
                                audio_elem = elem
                        if general_elem == None:
                            ErrorMsg("mediainfo_cli XML output does not have a <track> element of type 'General' for file: \""+file+"\"")
                        else:

                            _elem = general_elem.find("Format")
                            if _elem != None:
                                movie["container_format"] = _elem.text
                                movie["idContainerFormat"] = GetIdContainerFormat(_elem.text, ufile_w)

                            _elem = general_elem.find("Movie_name")
                            if _elem != None:
                                title_tag = _elem.text

                                movie["title_tag"] = title_tag

                                # Strip (year) and (qblock) and any rest from title tag

                                title = title_tag                                         # initially, the full tag
                                _pqblockend = title.rfind(")")                            # last ")" must be end of (qblock)
                                if _pqblockend >= 0:
                                    _title = title[0:_pqblockend+1]                       # remove stuff after (qblock)
                                    if re.match(".*\(.*(HD|HQ|SD).* [0-9]+x[0-9]+.*\)",_title):
                                        title = _title
                                        _pqblockbegin = title.rfind("(")
                                        if _pqblockbegin >= 0:
                                            title = title[0:_pqblockbegin].strip(" ")     # remove (qblock)
                                            m = re.match("(.*)\(([0-9]{4})\)(.*)",title)  # detect (year) in title
                                            if m != None:
                                                _t1, _year, _t2 = m.groups()
                                                title = _t1 + _t2                         # remove (year)
                                                title = title.replace("  "," ").replace(" , ",", ").strip(" ")

                                movie["title"] = title

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
                            ErrorMsg("mediainfo_cli XML output does not have a <track> element of type 'Video' for file: \""+file+"\"")
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

                            movie["idVideoFormat"] = GetIdVideoFormat(_format, _profile, ufile_w)

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
                                _v = _elem.text   # e.g. "16:9" or "1.25"
                                _colon = _v.find(":")
                                if _colon >= 0:
                                    # we assume there is a number before and after the colon
                                    _v = float(_v[0:_colon]) / float(_v[_colon+1:len(_v)])
                                else:
                                    _v = float(_v)
                                movie["video_dar"] = str(_v)

                            _elem = video_elem.find("Original_display_aspect_ratio")
                            if _elem != None:
                                _v = _elem.text   # e.g. "16:9" or "1.25"
                                _colon = _v.find(":")
                                if _colon >= 0:
                                    # we assume there is a number before and after the colon
                                    _v = float(_v[0:_colon]) / float(_v[_colon+1:len(_v)])
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
                                movie["idVideoFramerateMode"] = GetIdVideoFramerateMode(_elem.text, ufile_w)

                        if audio_elem == None:
                            ErrorMsg("mediainfo_cli XML output does not have a <track> element of type 'Audio' for file: \""+file+"\"")
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

                            movie["idAudioFormat"] = GetIdAudioFormat(_format, _profile, ufile_w)

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
                                movie["idAudioBitrateMode"] = GetIdAudioBitrateMode(_elem.text, ufile_w)

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


    # Further process title to detect series/episode information

    series_title = None
    episode_title = None
    running_number = None
    season_number = None
    episode_number = None

    m = re.match("^(.+) - ([0-9a-zA-Z]{1,4})\.([0-9a-zA-Z]{1,4}) - (.+)$",title)
    if m != None:
        # Msg("Debug: series/episode format #1: series_title, season_number, episode_number, episode_title = "+repr(m.groups())+" title = "+repr(title))
        series_title, season_number, episode_number, episode_title = m.groups()
    else:

        m = re.match("^(.+) - ([0-9a-zA-Z\-+.]{1,10}) - (.+)$",title)
        # This is also supposed to match e.g. "3.26+4.01" and treats that as a single running number
        if m != None:
            # Msg("Debug: series/episode format #2: series_title, running_number, episode_title = "+repr(m.groups())+" title = "+repr(title))
            series_title, running_number, episode_title = m.groups()
        else:

            m = re.match("^(.+)(, | - )((Teil|Folge|Episode|[Pp]art) [0-9a-zA-Z\-+.]{1,10})(: |, | - | )(.+)$",title)
            if m != None:
                # Msg("Debug: series/episode format #3: series_title, _dummy1, running_number, _dummy2, _dummy3, episode_title = "+repr(m.groups())+" title = "+repr(title))
                series_title, _dummy1, running_number, _dummy2, _dummy3, episode_title = m.groups()
                # Note, "(|)" also counts as a group; nested "()" count as a group following their parent
            else:

                m = re.match("^(.+)(, | - )((Teil|Folge|Episode|[Pp]art) [0-9a-zA-Z\-+.]{1,10})$",title)
                if m != None:
                    # Msg("Debug: series/episode format #4: series_title, _dummy1, running_number, _dummy2 = "+repr(m.groups())+" title = "+repr(title))
                    series_title, _dummy1, running_number, _dummy2 = m.groups()
                    # Note, "(|)" also counts as a group; nested "()" count as a group following their parent
                else:

                    # No series/episode information; values already set to None

                    if re.match(" (Teil|Folge|Episode|[Pp]art) ",title):
                        ErrorMsg("Movie title did not match any supported series/episode format but contains such keywords: "+repr(title))

    movie["series_title"] = series_title
    movie["episode_title"] = episode_title

    movie["season_number"] = season_number
    movie["episode_number"] = episode_number
    movie["running_number"] = running_number

    return movie


#------------------------------------------------------------------------------
def UpdateFile(file):

    Msg("Updating file: \""+file+"\" ...")

    movie = GetMovieInfo(file)

    # Msg("Debug: movie = "+str(movie))

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
    cv += "TitleTag = %(title_tag)s, "
    cv += "TitleFile = %(fn_title)s, "
    cv += "Title = %(title)s, "
    # cv += "ReleaseYearTag = '', "             # TBD: Get this value from MediaInfo
    cv += "ReleaseYearFile = %(fn_year)s, "
    cv += "ReleaseYear = %(fn_year)s, "
    cv += "SeriesTitle = %(series_title)s, "
    cv += "EpisodeTitle = %(episode_title)s, "
    cv += "SeasonNumber = %(season_number)s, "
    cv += "EpisodeNumber = %(episode_number)s, "
    cv += "RunningNumber = %(running_number)s"

    # movie["fn_threed"]+", "
    # movie["fn_partial"]+", "

    sql = "UPDATE Medium SET "+cv+" WHERE FilePath = %(file_path)s AND idCabinet = %(idCabinet)s"
    #Msg("Debug: sql = "+sql)

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)

    medium_cursor.execute(sql,movie)

    medium_cursor.close()

    movies_conn.commit()

#------------------------------------------------------------------------------
def AddFile(file):

    global movies_conn

    Msg("Adding file: \""+file+"\" ...")

    movie = GetMovieInfo(file)

    # Msg("Debug: movie = "+str(movie))

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
    now = str(datetime.datetime.now())[0:19]
    c += "TSUpdated, "
    v += "'"+now+"', "
    c += "TSVerified, "
    v += "'"+now+"', "
    c += "TitleTag, "
    v += "%(title_tag)s, "
    c += "TitleFile, "
    v += "%(fn_title)s, "
    c += "Title, "
    v += "%(title)s, "
    # c += "ReleaseYearTag, "
    # v +=                                    # TBD: Get this value from MediaInfo
    c += "ReleaseYearFile, "
    v += "%(fn_year)s, "
    c += "ReleaseYear, "
    v += "%(fn_year)s, "
    c += "SeriesTitle, "
    v += "%(series_title)s, "
    c += "EpisodeTitle, "
    v += "%(episode_title)s, "
    c += "SeasonNumber, "
    v += "%(season_number)s, "
    c += "EpisodeNumber, "
    v += "%(episode_number)s, "
    c += "RunningNumber"
    v += "%(running_number)s"

    # movie["fn_threed"]+", "
    # movie["fn_partial"]+", "

    sql = "INSERT INTO Medium ("+c+") VALUES ( "+v+")"
    # Msg("Debug: sql = "+sql)

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)

    medium_cursor.execute(sql,movie)

    medium_cursor.close()

    movies_conn.commit()


#------------------------------------------------------------------------------
def RemoveFile(file):

    global movies_conn

    Msg("Removing file: \""+file+"\" ...")

    ufile_w = unicode(file.decode("cp1250")) # file names on Windows are returned to Python in cp1250.

    # Split file path into UNC resource name and local file path
    _spos = ufile_w.find("\\",2)         # 0-based position of first backslash after initial "\\" (i.e. between server and share name)
    _ppos = ufile_w.find("\\",_spos+1)   # 0-based position of backslash that separates UNC resource name and local file path
    if ufile_w[0:2] == "\\\\" and _spos > 0 and _ppos > 0:
        ures_w = ufile_w[0:_ppos]        # UNC resource name (e.g. \\192.168.0.12\share)
        upath_w = ufile_w[_ppos:]        # local file path on the UNC resource, with leading backslash
    else:
        ErrorMsg("File path does not start with UNC resource name: "+ufile_w)
        ures_w = None
        upath_w = None


    movie = dict()
    movie["idCabinet"] = str(GetIdCabinet(ures_w, file))
    movie["upath_w"] = upath_w

    sql = "DELETE FROM Medium WHERE idCabinet = %(idCabinet)s AND FilePath = %(upath_w)s"
    # Msg("Debug: sql = "+sql)

    medium_cursor = movies_conn.cursor(MySQLdb.cursors.Cursor)

    medium_cursor.execute(sql,movie)

    medium_cursor.close()

    movies_conn.commit()


#------------------------------------------------------------------------------
def GetIdVideoQuality(name, file):

    global idvideoquality_dict

    if name == None:
        id = None
        ErrorMsg("No video quality in filename of movie file: "+file)
    else:
        if name in idvideoquality_dict:
            id = idvideoquality_dict[name]
        else:
            id = None
            ErrorMsg("Unknown video quality '"+name+"' in filename of movie file: "+file)

    return id

#------------------------------------------------------------------------------
def GetIdContainerFormat(field_value, file):

    global idcontainerformat_dict

    if field_value in idcontainerformat_dict:
        id = idcontainerformat_dict[field_value]
    else:
        id = None
        ErrorMsg("Unknown container format field value '"+str(field_value)+"' in movie file: "+file)

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
        ErrorMsg("Unknown video format field value '"+str(format_field_value)+"' or profile field value '"+str(profile_field_value)+"' in movie file: "+file)

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
        ErrorMsg("Unknown audio format field value '"+str(format_field_value)+"' or profile field value '"+str(profile_field_value)+"' in movie file: "+file)

    return id

#------------------------------------------------------------------------------
def GetIdVideoFramerateMode(field_value, file):

    global idvideoframeratemode_dict

    if field_value in idvideoframeratemode_dict:
        id = idvideoframeratemode_dict[field_value]
    else:
        id = None
        ErrorMsg("Unknown video framerate mode field value '"+str(field_value)+"' in movie file: "+file)

    return id

#------------------------------------------------------------------------------
def GetIdAudioBitrateMode(field_value, file):

    global idaudiobitratemode_dict

    if field_value in idaudiobitratemode_dict:
        id = idaudiobitratemode_dict[field_value]
    else:
        id = None
        ErrorMsg("Unknown audio bitrate mode field value '"+str(field_value)+"' in movie file: "+file)

    return id

#------------------------------------------------------------------------------
def GetIdCabinet(smb_server_resource, file):

    global idcabinet_dict

    if smb_server_resource in idcabinet_dict:
        id = idcabinet_dict[smb_server_resource]
    else:
        id = None
        ErrorMsg("Media cabinet for SMB server resource '"+str(smb_server_resource)+"' not found in movie database, file: "+file)

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
        if arg == "-?" or arg == "--help":
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

#
# Process the specified sources
#

# Translation table for Unicode characters that make trouble in XML parsing
xmlrep_from_chars = \
    u"\u0000\u0001\u0002\u0003\u0004\u0005\u0006\u0007\u0008\u000b\u000c\u000e\u000f" + \
    u"\u0010\u0011\u0012\u0013\u0014\u0015\u0016\u0017\u0018\u0019\u001a\u001b\u001c\u001d\u001e\u001f"
#xmlrep_to_char = u"?"
xmlrep_trans = dict( (ord(_c), u"U+"+format(ord(_c),"04X")) for _c in xmlrep_from_chars)


movies = []

# List the files on the various sources
Msg("Scanning source locations for movie files...")
sourcepath_list = []     # list of source files
sourcepath_dict = dict() # dictionary of source files
                         # key: file path (UNC resource name + local path)
                         # value: object:
                         #   status: status value, see file_source

for file_source in file_sources:

    source_res_w = file_source["res"]
    source_dir_w = file_source["dir"]
    source_patterns = file_source["patterns"]
    source_status = file_source["status"]

    source_path_w = source_res_w+source_dir_w
    # source_path_u = source_path_w.replace("\\","/")

    Msg("Source location: \""+source_path_w+"\" ...")

    _files = []
    for pattern in source_patterns:
        _files += rglob(source_path_w, pattern)
    _files = sorted(_files)
    sourcepath_list += _files

    for _file in _files:
        sourcepath_dict[_file] = { "status": source_status }

Msg("Found "+str(len(sourcepath_list))+" movie files in source locations")


# Connection to movie database
movies_conn = MySQLdb.connect(host=mysql_host,user=mysql_user,db=mysql_db,use_unicode=True)


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
# Msg("Debug: idvideoquality_dict = "+str(idvideoquality_dict))

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
# Msg("Debug: idcontainerformat_dict = "+str(idcontainerformat_dict))


# Build idvideoformat_dict dictionary from FixedVideoFormat table in movie database
_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute("SELECT idVideoFormat,FormatFieldValue,ProfileFieldValue FROM FixedVideoFormat ORDER BY idVideoFormat")
_rows = _cursor.fetchall()
_cursor.close()
fixedvideoformat_list = _rows   # array that is a copy of table FixedVideoFormat. Each row is an array entry that is
                                # an object with properties for the following columns of that table:
                                #   idVideoFormat, FormatFieldValue, ProfileFieldValue.
# Msg("Debug: fixedvideoformat_list = "+str(fixedvideoformat_list))


# Build idaudioformat_dict dictionary from FixedAudioFormat table in movie database
_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
_cursor.execute("SELECT idAudioFormat,FormatFieldValue,ProfileFieldValue FROM FixedAudioFormat ORDER BY idAudioFormat")
_rows = _cursor.fetchall()
_cursor.close()
fixedaudioformat_list = _rows   # array that is a copy of table FixedAudioFormat. Each row is an array entry that is
                                # an object with properties for the following columns of that table:
                                #   idAudioFormat, FormatFieldValue, ProfileFieldValue.
# Msg("Debug: fixedaudioformat_list = "+str(fixedaudioformat_list))


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
# Msg("Debug: idvideoframeratemode_dict = "+str(idvideoframeratemode_dict))


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
# Msg("Debug: idaudiobitratemode_dict = "+str(idaudiobitratemode_dict))


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
    # Msg("Debug: cabinet_row = "+str(cabinet_row))
    res = "\\\\"+cabinet_row["SMBServerHost"]+"\\"+cabinet_row["SMBServerShare"]
    id = cabinet_row["idCabinet"]
    cabinet_dict[id] = res
    idcabinet_dict[res] = id
# Msg("Debug: cabinet_dict = "+str(cabinet_dict))
# Msg("Debug: idcabinet_dict = "+str(idcabinet_dict))


# Get all movie files known in movie database, and build mediumpath_dict
medium_cursor = movies_conn.cursor(MySQLdb.cursors.DictCursor)
medium_cursor.execute("SELECT FilePath,TSUpdated,TSVerified,idCabinet FROM Medium WHERE idMediumType = 'FILE'")
mediumpath_dict = dict() # dictionary of medium files in movie database
                         # key: file path
                         # value: object:
                         #   updated: date where medium row was last updated
                         #   verified: date where file existence was last verified
while True:
    medium_row = medium_cursor.fetchone()
    if medium_row == None:
        break
    idCabinet = medium_row["idCabinet"]
    res = cabinet_dict[idCabinet]
    obj = { "updated": medium_row["TSUpdated"], "verified": medium_row["TSVerified"] }
    path = res+medium_row["FilePath"]
    mediumpath_dict[path] = obj
medium_cursor.close()

Msg("Found "+str(len(mediumpath_dict))+" movie files in movie database")

# Msg("Debug: mediumpath_dict = "+str(mediumpath_dict))

movies_conn.commit()

Msg("Updating movie database from source locations...")

for file in sourcepath_list:

    try:
        file_modified_dt = datetime.datetime.fromtimestamp(os.stat(file).st_mtime)
        file_no_longer_exists = False
    except:
        file_modified_dt = None
        file_no_longer_exists = True

    if file_no_longer_exists:

        Msg("Warning: Skipping movie file that was deleted since scanning source location: \""+file+"\" ...")

    else:

        basefile = os.path.basename(file)
        m = re.match("^.+\(.*(FHD|HD|HQ|SD)(\+(HD|HQ|SD))?(-low)? [0-9]+x[0-9]+.*\)\..+$",basefile)
        if m == None:

            Msg("Skipping file with unknown file name format: \""+file+"\" ...")

        else:

            if file in mediumpath_dict:

                # Msg("Debug: file_modified_dt = "+str(file_modified_dt)+", type = "+str(type(file_modified_dt)))


                medium_updated_dt = mediumpath_dict[file]["updated"] # datetime type
                if file_modified_dt > medium_updated_dt or update_all:
                    UpdateFile(file)
                else:
                    pass
                    # Msg("Debug: Skipping unchanged movie file: \""+file+"\" ...")
            else:
                AddFile(file)

for file in mediumpath_dict:
    if file not in sourcepath_list:
        RemoveFile(file)

if num_errors > 0:
    ErrorMsg("Finished with "+str(num_errors)+" errors.")
    exit(12)
else:
    exit(0)

