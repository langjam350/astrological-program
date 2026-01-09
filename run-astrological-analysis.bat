@echo off
setlocal enabledelayedexpansion

set "BIRTH_DATE="
set "BIRTH_TIME="
set "BIRTH_LOCATION="
set "CURRENT_LOCATION="

:parse_args
if "%~1"=="" goto validate_args
if "%~1"=="-BD" (
    set "BIRTH_DATE=%~2"
    shift
    shift
    goto parse_args
)
if "%~1"=="-BT" (
    set "BIRTH_TIME=%~2"
    shift
    shift
    goto parse_args
)
if "%~1"=="-BL" (
    set "BIRTH_LOCATION=%~2"
    shift
    shift
    goto parse_args
)
if "%~1"=="-CL" (
    set "CURRENT_LOCATION=%~2"
    shift
    shift
    goto parse_args
)
echo Unknown parameter: %~1
echo Usage: %0 -BD birth_date -BT birth_time -BL "birth_city;state" -CL "current_city;state"
exit /b 1

:validate_args
if "%BIRTH_DATE%"=="" (
    echo Error: Birth Date parameter -BD is required
    echo Usage: %0 -BD birth_date -BT birth_time -BL "birth_city;state" -CL "current_city;state"
    exit /b 1
)
if "%BIRTH_TIME%"=="" (
    echo Error: Birth Time parameter -BT is required
    echo Usage: %0 -BD birth_date -BT birth_time -BL "birth_city;state" -CL "current_city;state"
    exit /b 1
)
if "%BIRTH_LOCATION%"=="" (
    echo Error: Birth Location parameter -BL is required
    echo Usage: %0 -BD birth_date -BT birth_time -BL "birth_city;state" -CL "current_city;state"
    exit /b 1
)
if "%CURRENT_LOCATION%"=="" (
    echo Error: Current Location parameter -CL is required
    echo Usage: %0 -BD birth_date -BT birth_time -BL "birth_city;state" -CL "current_city;state"
    exit /b 1
)

echo Starting Weekly Astrological Analysis...
echo Birth Date: %BIRTH_DATE%
echo Birth Time: %BIRTH_TIME%
echo Birth Location: %BIRTH_LOCATION%
echo Current Location: %CURRENT_LOCATION%
echo.

python astrological-calculations\astrological_analyzer.py "%BIRTH_DATE%" "%BIRTH_TIME%" "%BIRTH_LOCATION%" "%CURRENT_LOCATION%"

if %errorlevel% neq 0 (
    echo Error: Analysis failed
    exit /b 1
)

echo Weekly analysis complete.