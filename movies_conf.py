#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
# Configuration parameters for movies_* scripts
#

output_cp  = "cp850"            # code page used for output messages
cmdline_cp = "cp1250"           # code page used for command line parameters

mysql_host = "192.168.0.12"     # IP addess or hostname of the MySQL server
mysql_port = None               # port of the MySQL sever, None for default port (3306)
mysql_db   = "movies"           # movies database in the MySQL sever
mysql_user = "pyuser"           # user to be used for logon to the MySQL sever
mysql_pass = None               # password to be used for logon to the MySQL sever, None for no password

fileserver_share = "\\\\"+mysql_host+"\\share"       # UNC resource of file server
