@echo off
setlocal

set "BIRTH_DATE="
set "BIRTH_TIME="
set "BIRTH_LOCATION="
set "CURRENT_LOCATION="
set "AI_PROVIDER="
set "REPORT_MODE=weekly"

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
if "%~1"=="-T" (
    set "REPORT_MODE=transits"
    shift
    goto parse_args
)
if "%~1"=="-BW" (
    set "REPORT_MODE=biwheel"
    shift
    goto parse_args
)
echo Unknown parameter: %~1
echo Usage: %0 [-BD date] [-BT time] [-BL "city~state"] [-CL "city~state"] [-AI provider] [-T^|-BW]
echo All parameters are optional - you will be prompted for any missing values.
exit /b 1

:prompt_missing
if "%BIRTH_DATE%"=="" set /p "BIRTH_DATE=Enter birth date (YYYY-MM-DD): "
if "%BIRTH_DATE%"=="" (
    echo Error: Birth date is required.
    exit /b 1
)

if "%BIRTH_TIME%"=="" set /p "BIRTH_TIME=Enter birth time (HH:MM, 24-hour format): "
if "%BIRTH_TIME%"=="" (
    echo Error: Birth time is required.
    exit /b 1
)

if "%BIRTH_LOCATION%"=="" set /p "BIRTH_LOCATION=Enter birth location (City~State, e.g. New York~NY): "
if "%BIRTH_LOCATION%"=="" (
    echo Error: Birth location is required.
    exit /b 1
)

if "%CURRENT_LOCATION%"=="" set /p "CURRENT_LOCATION=Enter current location (City~State, e.g. Los Angeles~CA): "
if "%CURRENT_LOCATION%"=="" (
    echo Error: Current location is required.
    exit /b 1
)

if not "%AI_PROVIDER%"=="" goto map_provider

echo.
echo AI Enhancement Options:
echo   1. none    - No AI enhancement (standard reports)
echo   2. local   - Local LLM (Ollama)
echo   3. openai  - OpenAI (requires API key in llm_config.json)
echo   4. claude  - Anthropic Claude (requires API key in llm_config.json)
echo   5. gemini  - Google Gemini (requires API key in llm_config.json)
echo.
set /p "AI_PROVIDER=Select AI provider [none/local/openai/claude/gemini]: "

:map_provider
if "%AI_PROVIDER%"=="" set "AI_PROVIDER=none"
if "%AI_PROVIDER%"=="1" set "AI_PROVIDER=none"
if "%AI_PROVIDER%"=="2" set "AI_PROVIDER=local"
if "%AI_PROVIDER%"=="3" set "AI_PROVIDER=openai"
if "%AI_PROVIDER%"=="4" set "AI_PROVIDER=claude"
if "%AI_PROVIDER%"=="5" set "AI_PROVIDER=gemini"

echo.
echo Starting Weekly Astrological Analysis...
echo Birth Date: %BIRTH_DATE%
echo Birth Time: %BIRTH_TIME%
echo Birth Location: %BIRTH_LOCATION%
echo Current Location: %CURRENT_LOCATION%
echo AI Provider: %AI_PROVIDER%
echo.

py -3 astrological-calculations\astrological_analyzer.py "%BIRTH_DATE%" "%BIRTH_TIME%" "%BIRTH_LOCATION%" "%CURRENT_LOCATION%" "%AI_PROVIDER%" "%REPORT_MODE%"

if %errorlevel% neq 0 (
    echo Error: Analysis failed
    exit /b 1
)

echo Weekly analysis complete.
