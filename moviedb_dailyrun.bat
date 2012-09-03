@setlocal
@echo off
if not exist L:\admauto\*.* net use L: \\192.168.0.12\share
L:
cd L:\admauto
call moviedb_scan_files -v >moviedb_dailyrun.log 2>&1
call moviedb_import_movies -v -f MyMDb_šbersicht.xls -s Sheet0 -l mymdb >>moviedb_dailyrun.log 2>&1
call moviedb_link_movies -v >>moviedb_dailyrun.log 2>&1
call moviedb_gen_mymdb_missing -v >>moviedb_dailyrun.log 2>&1
call moviedb_gen_movielist -v >>moviedb_dailyrun.log 2>&1
