@echo off
setlocal enabledelayedexpansion

set "BIRTH_DATE="
set "BIRTH_TIME="
set "BIRTH_LOCATION="
set "CURRENT_LOCATION="
set "AI_PROVIDER="

:parse_args
if "%~1"=="" goto prompt_missing
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
if "%~1"=="-AI" (
    set "AI_PROVIDER=%~2"
    shift
    shift
    goto parse_args
)
echo Unknown parameter: %~1
echo Usage: %0 [-BD date] [-BT time] [-BL "city;state"] [-CL "city;state"] [-AI provider]
echo All parameters are optional - you will be prompted for any missing values.
exit /b 1

:prompt_missing
if "%BIRTH_DATE%"=="" (
    set /p "BIRTH_DATE=Enter birth date (YYYY-MM-DD): "
)
if "%BIRTH_DATE%"=="" (
    echo Error: Birth date is required.
    exit /b 1
)
if "%BIRTH_TIME%"=="" (
    set /p "BIRTH_TIME=Enter birth time (HH:MM, 24-hour format): "
)
if "%BIRTH_TIME%"=="" (
    echo Error: Birth time is required.
    exit /b 1
)
if "%BIRTH_LOCATION%"=="" (
    set /p "BIRTH_LOCATION=Enter birth location (City;State, e.g. New York;NY): "
)
if "%BIRTH_LOCATION%"=="" (
    echo Error: Birth location is required.
    exit /b 1
)
if "%CURRENT_LOCATION%"=="" (
    set /p "CURRENT_LOCATION=Enter current location (City;State, e.g. Los Angeles;CA): "
)
if "%CURRENT_LOCATION%"=="" (
    echo Error: Current location is required.
    exit /b 1
)
if "%AI_PROVIDER%"=="" (
    echo.
    echo AI Enhancement Options:
    echo   1. none    - No AI enhancement (standard reports)
    echo   2. local   - Local LLM (Ollama)
    echo   3. openai  - OpenAI (requires API key in llm_config.json)
    echo   4. claude  - Anthropic Claude (requires API key in llm_config.json)
    echo   5. gemini  - Google Gemini (requires API key in llm_config.json)
    echo.
    set /p "AI_PROVIDER=Select AI provider [none/local/openai/claude/gemini]: "
)
if "%AI_PROVIDER%"=="" set "AI_PROVIDER=none"

echo.
echo Starting Weekly Astrological Analysis...
echo Birth Date: %BIRTH_DATE%
echo Birth Time: %BIRTH_TIME%
echo Birth Location: %BIRTH_LOCATION%
echo Current Location: %CURRENT_LOCATION%
echo AI Provider: %AI_PROVIDER%
echo.

python astrological-calculations\astrological_analyzer.py "%BIRTH_DATE%" "%BIRTH_TIME%" "%BIRTH_LOCATION%" "%CURRENT_LOCATION%" "%AI_PROVIDER%"

if %errorlevel% neq 0 (
    echo Error: Analysis failed
    exit /b 1
)

echo Weekly analysis complete.
