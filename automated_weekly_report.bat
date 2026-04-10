@echo off
cd /d "%~dp0"

echo Starting automated LLM-enhanced astrological report generation...
echo Time: %date% %time%

REM Check if LLM service is available first
echo Checking LLM availability...
python -c "from llm_enhancer import LLMConfigManager; import sys; cm = LLMConfigManager(); sys.exit(0 if cm.test_connection() else 1)"

if %errorlevel% equ 0 (
    echo LLM service confirmed - generating enhanced reports...

    REM Run the astrological analyzer with LLM enhancement priority
    python astrological-calculations\astrological_analyzer.py 2000-06-20 00:11 "Cincinatti;Ohio" "Las Vegas;Nevada"

    if %errorlevel% equ 0 (
        echo Enhanced report generation completed successfully

        REM Check if enhanced reports were actually created
        python -c "from pathlib import Path; p=Path('tosend'); print('✅ Enhanced reports found' if p.exists() and any(p.glob('*enhanced*')) else '⚠️ No enhanced reports found')"

        REM Process local delivery if configured
        python local_delivery_runner.py
    ) else (
        echo Report generation failed with error level %errorlevel%
        echo Check if your birth information is correct or if there are Python errors
    )
) else (
    echo LLM service not available - skipping automated report generation
    echo To fix this:
    echo 1. Make sure Ollama is installed and running
    echo 2. Run: ollama serve
    echo 3. Verify your model is available: ollama list
)

echo Automated task completed at %date% %time%
