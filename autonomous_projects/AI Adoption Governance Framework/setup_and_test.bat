@echo off
setlocal enabledelayedexpansion

echo Setting up AI Adoption Governance Framework...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
    echo Created virtual environment
)

REM Activate virtual environment
source venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

echo Dependencies installed successfully

REM Run tests
python -m pytest tests/ -v
if %ERRORLEVEL% EQU 0 (
    echo All tests passed!
    exit /b 0
) else (
    echo Tests failed
    exit /b 1
)
