@setlocal
@echo off
if not exist L:\admauto\*.* net use L: \\192.168.0.12\share
L:
cd L:\admauto
call movies_updatemedia -v >L:\admauto\movies_dailyrun.log 2>&1
call movies_updatemovies -v -f L:\admauto\MyMDb_šbersicht.xls -s Sheet0 -l mymdb >>L:\admauto\movies_dailyrun.log 2>&1
call movies_linkmovies -v >>L:\admauto\movies_dailyrun.log 2>&1
call movies_listformymdb -v >>L:\admauto\movies_dailyrun.log 2>&1
call movies_genlist -v >>L:\admauto\movies_dailyrun.log 2>&1
