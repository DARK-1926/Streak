@echo off
setlocal

cd /d "%~dp0"

if exist .venv (
    echo Activating existing venv...
    call .venv\Scripts\activate.bat
) else (
    echo Creating venv...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)

python -m pip install --quiet --upgrade pip

python -m pip install --quiet pytest pytest-json-report
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo Running tests...
python -m pytest --json-report --json-report-file=report.json -v
set EXITCODE=%ERRORLEVEL%

exit /b %EXITCODE%