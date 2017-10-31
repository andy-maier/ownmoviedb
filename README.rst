moviedb - Python utilities for creating and updating a movies database
======================================================================

Installation
------------

This package is a Python source distribution that is designed for installation as a Python site package:

1. Unpack the source distribution archive moviedb-N.M.U.zip into some directory.

2. Run the following command from the moviedb-N.M.U directory within the unpack directory:

     python setup.py build install

3. The unpack directory can then be deleted.


Change History
--------------

V1.4.0 2013-09-09
~~~~~~~~~~~~~~~~~

* Added support for .avi file extension (just .avi, not .div.avi or .mpg.avi)
  in ParseMovieFilename().
* Added support for more than one language in ParseMovieFilename().
* Added 'AE' and middle dot characters to normalization.
* Added directories to filepath_begin_list.
* Tolerate empty genres (e.g. caused by trailing comma, as in: "Action,").
* Added support for more than one audio stream.

V1.3.1 2013-05-19
~~~~~~~~~~~~~~~~~

* Renamed output CSV file to AM_MovieList.csv.
* Added DAR and ODAR columns to CSV file.

V1.3.0 2012-12-26
~~~~~~~~~~~~~~~~~

* Added support for .mkv and .flv
* Minor improvements in title handling.

V1.2.3a 2012-11-07
~~~~~~~~~~~~~~~~~~

* Added moviedb_tvbrowser_moviecheck.py.
* Added support for FolderPath column. (was originally in 1.2.0)
* Improved error message for unknown genre.

V1.2.2 2012-09-20
~~~~~~~~~~~~~~~~~

* Simplified and improved matching algorithm in moviedb_link_movies.py.
* Added fallback for movie title parsing: If no series/episode information in Kommentar,
  the title of the movie is parsed for series and episode information.

V1.2.1 2012-09-04
~~~~~~~~~~~~~~~~~

* Improved and fixed parsing of media file names.
* Improved and fixed parsing of movie titles; it is now consistent for titles
  from file names and titles from title tags.
* New module structure.
* Consistent version across the package.

V1.2.0
~~~~~~


V1.1.1 2012-08-12
~~~~~~~~~~~~~~~~~

* First version in SVN and with change history.


Todo List
---------

* Importing MyMDB movies

  - Parse series & episode information (comment / title)
  - Tolerate and ignore empty genre (generated from trailing comma, e.g. "a, b,")

* Link Movie and Medium:

  - On Error: Not linking movie file that matches more than one movie description by file title with description title
    -> Take Release Year into consideration.

* Add genre to Genre table: TV-Pilotfilm

* Checker (moviedb_check.py):

  - Upgrade to new module structure.
  - Review and improve checks it makes.

    - Desired DAR as stated in filename matches DAR/OriginalDAR meta-info (OriginalDAR has precedence)
    - Quality as stated in filename satisfies requirements w.r.t. sample width/height and video bitrate (see definition in movies spreadsheet)
    - uncut version of same quality present if cut versionis also present
    - SD version present if higher quality version is also present (for now, we accept duplicates for HQ and higher)
    - ...
  - Integrate moviedb_gen_missing.py into checker ?

* Setup:

  - Create database schema
    - From MySql Workbench data (if not, how to sync with Workbench data)?
    - How to deal with Genre content?
    - How to integrate with setup.py ?

* Integrate scrapers for movie descriptions.

* Integrate web pages.

* Improve error handling for failed database connection in all scripts

  For example this exception::

      Traceback (most recent call last):
       File "c:\copy\tools\bin\movies_updatemedia.py", line 1131, in <module>
         movies_conn = MySQLdb.connect(host=mysql_host,user=mysql_user,db=mysql_db,use_unicode=True)
       File "C:\Python27\lib\site-packages\MySQLdb\__init__.py", line 81, in Connect
         return Connection(*args, **kwargs)
       File "C:\Python27\lib\site-packages\MySQLdb\connections.py", line 187, in __init__
         super(Connection, self).__init__(*args, **kwargs2)
      _mysql_exceptions.OperationalError: (1130, "Host 'Andi-TP-LAN.fritz.box' is not allowed to connect to this MySQL server"

* Verify usage of parameters in moviedb/config.py

* Fix title parsing error::

      moviedb_scan_files Version 1.4.0

      File: "\\192.168.0.12\share\admauto\Andi-PC\Die Swingmaedchen, Teil 1 (HD 16x9).uncut.mpg.avi" ...
      Title in file: " Die Swingm„dchen (1/2)"

      Traceback (most recent call last):
      File "C:\Python27\Scripts\moviedb_scan_files.py", line 1029, in <module>
      AddFile(sourcepath)
      File "C:\Python27\Scripts\moviedb_scan_files.py", line 519, in AddFile
      movie = GetMovieInfo(moviefile_uncpath)
      File "C:\Python27\Scripts\moviedb_scan_files.py", line 275, in GetMovieInfo
      parsed_filename_tag = utils.ParseMovieFilename(title_tag,tolerate_noext=True)
      File "C:\Python27\lib\site-packages\moviedb\utils.py", line 475, in ParseMovieFilename
      m = re.match(r"[0-9]+)x([0-9]+)$",qblock_words[0])
      IndexError: list index out of range

* Fix "just-end" error in admauto.

* Improve error handling for this situation::

      moviedb_scan_files Version 1.4.1
      Scanning source locations for movie files...
      Source location: "\\192.168.0.12\share\admauto" ...
      Source location: "\\192.168.0.12\share\Movies\MissingParts" ...
      Source location: "\\192.168.0.12\share\Movies\LowResolution+Duplicates" ...
      Source location: "\\192.168.0.12\share\Movies\share" ...
      Source location: "\\192.168.0.12\share\Movies\share.disabled" ...
      Found 10474 movie files in source locations
      Traceback (most recent call last):
        File "C:\Python27\Scripts\moviedb_scan_files.py", line 878, in <module>
          db=config.mysql_db, use_unicode=True, charset='utf8')
        File "C:\Python27\lib\site-packages\MySQLdb\__init__.py", line 81, in Connect
          return Connection(*args, **kwargs)
        File "C:\Python27\lib\site-packages\MySQLdb\connections.py", line 187, in __init__
          super(Connection, self).__init__(*args, **kwargs2)
      _mysql_exceptions.OperationalError: (2013, "Lost connection to MySQL server at 'reading authorization packet', system error: 2")

* pylint

* Improve module structure
