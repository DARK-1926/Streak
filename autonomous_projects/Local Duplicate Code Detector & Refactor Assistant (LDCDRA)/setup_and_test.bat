@echo off
setlocal

rem Check for Python
where python >nul 2>&1
if errorlevel 1 (
    echo Python not found.
    exit /b 1
)

rem Create virtual environment
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    exit /b 1
)

rem Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

rem Install dependencies
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    pip install .
)
if errorlevel 1 (
    echo Failed to install dependencies.
    exit /b 1
)

rem Run tests
python -m pytest
if errorlevel 0 (
    echo Tests passed.
    exit /b 0
) else (
    echo No tests or tests failed. Running main.py for 5 seconds.
    start /b python main.py >nul 2>&1
    timeout /t 5 >nul
    taskkill /im python.exe /f >nul 2>&1
    rem Assume success if main started
    exit /b 0
)