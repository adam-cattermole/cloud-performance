@ECHO OFF
SETLOCAL
SET "sourcedir=out"
SET /a fcount=100
SET /a llimit=250000
SET /a lcount=%llimit%
FOR /f "usebackqdelims=" %%a IN ("%sourcedir%\price_info.txt") DO (
 CALL :select
 FOR /f "tokens=1*delims==" %%b IN ('set dfile') DO IF /i "%%b"=="dfile" >>"%%c" ECHO(%%a
)
GOTO :EOF
:select
SET /a lcount+=1
IF %lcount% lss %llimit% GOTO :EOF
SET /a lcount=0
SET /a fcount+=1
SET "dfile=%sourcedir%\file%fcount:~-2%.txt"
GOTO :EOF
