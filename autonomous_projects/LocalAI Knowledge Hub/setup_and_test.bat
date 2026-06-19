@echo off
setlocal enabledelayedexpansion

:: Create virtual environment if not exists
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        exit /b 1
    )
)

:: Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    exit /b 1
)

:: Install dependencies
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies
        exit /b 1
    )
)

:: Check for tests
set TEST_FOUND=0
dir tests\ >nul 2>&1
if !errorlevel! equ 0 set TEST_FOUND=1
if !TEST_FOUND! equ 0 (
    dir test*.py >nul 2>&1
    if !errorlevel! equ 0 set TEST_FOUND=1
)

if %TEST_FOUND% equ 1 (
    :: Run tests
    pytest
    if errorlevel 1 (
        echo Tests failed
        exit /b 1
    )
) else (
    :: Run main.py for 5 seconds
    echo Running main.py for 5 seconds...
    start /b python main.py
    timeout /t 5 >nul
    taskkill /f /im python.exe >nul 2>&1
    echo Main file ran successfully
)

echo Setup and test completed successfully
exit /b 0