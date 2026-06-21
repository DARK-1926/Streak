@echo off
REM Setup Python virtual environment
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    exit /b 1
)

REM Activate the virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

REM Upgrade pip
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Failed to upgrade pip.
    exit /b 1
)

REM Install required dependencies
pip install pytest pytest-json-report
if errorlevel 1 (
    echo Failed to install dependencies.
    exit /b 1
)

REM Run unit tests with JSON report
pytest --json-report --json-report-file=report.json
if %errorlevel% equ 0 (
    exit /b 0
) else (
    exit /b 1
)