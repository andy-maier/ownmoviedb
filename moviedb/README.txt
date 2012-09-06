
moviedb - Python utilities for creating and updating a movies database


Installation:

  This package is a Python source distribution that is designed for installation as a Python site package:

  1. Unpack the source distribution archive moviedb-N.M.U.zip into some directory.
  2. Run the following command from the moviedb-N.M.U directory within the unpack directory:
       python setup.py build install
  3. The unpack directory can then be deleted.


Change History:

  V1.2.2 2012-09-05
    Simplified and improved matching algorithm in moviedb_link_movies.py.

  V1.2.1 2012-09-04
    Improved and fixed parsing of media file names.
    Improved and fixed parsing of movie titles; it is now consistent for titles
      from file names and titles from title tags.
    New module structure.
    Consistent version across the package.

  V1.1.1 2012-08-12
    First version in SVN and with change history.


Todo List:

  - Add genre to Genre table: TV-Pilotfilm

  - Checker (moviedb_check.py):
    - Upgrade to new module structure.
    - Review and improve checks it makes.
    - Integrate moviedb_gen_missing.py into checker ?

  - Setup:
    - Create database schema
       From MySql Workbench data (if not, how to sync with Workbench data)?
       How to deal with Genre content?
       How to integrate with setup.py ?

  - Integrate scrapers for movie descriptions.

  - Integrate web pages.

  - Infrastructure improvements in all scripts:
    - Improve error handling for failed database connection
      For example this exception:
        Traceback (most recent call last):
         File "c:\copy\tools\bin\movies_updatemedia.py", line 1131, in <module>
           movies_conn = MySQLdb.connect(host=mysql_host,user=mysql_user,db=mysql_db,use_unicode=True)
         File "C:\Python27\lib\site-packages\MySQLdb\__init__.py", line 81, in Connect
           return Connection(*args, **kwargs)
         File "C:\Python27\lib\site-packages\MySQLdb\connections.py", line 187, in __init__
           super(Connection, self).__init__(*args, **kwargs2)
        _mysql_exceptions.OperationalError: (1130, "Host 'Andi-TP-LAN.fritz.box' is not allowed to connect to this MySQL server"
    - Verify usage of parameters in moviedb/config.py
