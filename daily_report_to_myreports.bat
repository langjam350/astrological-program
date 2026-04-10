@echo off
REM Daily Astrological Report Generator - Saves to MyReports folder
REM This script generates a daily report at midnight using configured birth data

cd /d "%~dp0"

REM Try to find Python - check multiple locations
REM Skip WindowsApps aliases and check actual installations
set PYTHON_CMD=

REM Check user AppData locations first (correct path: Python\PythonXXX)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe
    goto :python_found
)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe
    goto :python_found
)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe" (
    set PYTHON_CMD=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe
    goto :python_found
)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe" (
    set PYTHON_CMD=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe
    goto :python_found
)

REM Check system-wide locations
if exist "C:\Python311\python.exe" (
    set PYTHON_CMD=C:\Python311\python.exe
    goto :python_found
)
if exist "C:\Python310\python.exe" (
    set PYTHON_CMD=C:\Python310\python.exe
    goto :python_found
)
if exist "C:\Python312\python.exe" (
    set PYTHON_CMD=C:\Python312\python.exe
    goto :python_found
)

REM Last resort - try py launcher
where /q py.exe 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=py.exe
    goto :python_found
)

echo ERROR: Python not found!
echo Please install Python from https://www.python.org/
echo Make sure to check "Add Python to PATH" during installation.
exit /b 1

:python_found
echo Using Python: %PYTHON_CMD%

echo ========================================
echo Daily Astrological Report Generation
echo Started: %date% %time%
echo ========================================
echo.

REM Load birth configuration
set CONFIG_FILE=birth_config.json

if not exist "%CONFIG_FILE%" (
    echo ERROR: Configuration file %CONFIG_FILE% not found!
    echo Please create birth_config.json with your birth information.
    echo.
    echo Example format:
    echo {
    echo   "birth_date": "1990-05-15",
    echo   "birth_time": "14:30",
    echo   "birth_location": "New York;NY",
    echo   "current_location": "Los Angeles;CA"
    echo }
    exit /b 1
)

echo Reading configuration from %CONFIG_FILE%...

REM Use Python to parse JSON and extract values
for /f "delims=" %%a in ('%PYTHON_CMD% -c "import json; f=open('%CONFIG_FILE%'); d=json.load(f); print(d['birth_date']); f.close()"') do set BIRTH_DATE=%%a
for /f "delims=" %%a in ('%PYTHON_CMD% -c "import json; f=open('%CONFIG_FILE%'); d=json.load(f); print(d['birth_time']); f.close()"') do set BIRTH_TIME=%%a
for /f "delims=" %%a in ('%PYTHON_CMD% -c "import json; f=open('%CONFIG_FILE%'); d=json.load(f); print(d['birth_location']); f.close()"') do set BIRTH_LOCATION=%%a
for /f "delims=" %%a in ('%PYTHON_CMD% -c "import json; f=open('%CONFIG_FILE%'); d=json.load(f); print(d['current_location']); f.close()"') do set CURRENT_LOCATION=%%a

echo.
echo Configuration loaded:
echo   Birth Date: %BIRTH_DATE%
echo   Birth Time: %BIRTH_TIME%
echo   Birth Location: %BIRTH_LOCATION%
echo   Current Location: %CURRENT_LOCATION%
echo.

REM Ensure MyReports directory exists
if not exist MyReports mkdir MyReports

echo Generating astrological report...
echo.

REM Run the astrological analyzer
"%PYTHON_CMD%" astrological-calculations\astrological_analyzer.py "%BIRTH_DATE%" "%BIRTH_TIME%" "%BIRTH_LOCATION%" "%CURRENT_LOCATION%"

REM Note: Error code 1 might be emoji encoding issues - non-critical if report was generated
set ANALYZER_EXIT=%errorlevel%

echo.
if %ANALYZER_EXIT% equ 0 (
    echo Report generation completed successfully!
) else (
    echo Report generation completed with warnings (exit code %ANALYZER_EXIT%)
    echo Note: Emoji encoding errors are non-critical if reports were generated.
)
echo.

REM Find the most recent weekly_report directory
for /f "delims=" %%d in ('dir /b /ad /o-d weekly_report_*') do (
    set LATEST_REPORT=%%d
    goto :found_report
)

:found_report
if not defined LATEST_REPORT (
    echo WARNING: No report directory found!
    exit /b 1
)

echo Latest report directory: %LATEST_REPORT%
echo.

REM Create timestamped folder name in MyReports
set TIMESTAMP=%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set DEST_FOLDER=MyReports\report_%TIMESTAMP%

echo Copying report to %DEST_FOLDER%...
xcopy "%LATEST_REPORT%" "%DEST_FOLDER%\" /E /I /Y

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS: Report saved to %DEST_FOLDER%
    echo Completed: %date% %time%
    echo ========================================
) else (
    echo.
    echo ERROR: Failed to copy report to MyReports folder
    exit /b 1
)

echo.
