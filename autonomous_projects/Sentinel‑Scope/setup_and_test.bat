@echo off
setlocal

:: Create virtual environment if it doesn't exist
if not exist venv (
    python -m venv venv
)

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Install dependencies
pip install -r requirements.txt

:: Check for test files
dir /b /s test_*.py >nul 2>&1
if %errorlevel%==0 (
    set TESTS_FOUND=1
) else (
    dir /b /s tests\*.py >nul 2>&1
    if %errorlevel%==0 (
        set TESTS_FOUND=1
    ) else (
        set TESTS_FOUND=0
    )
)

:: Run tests if found
if "%TESTS_FOUND%"=="1" (
    python -m unittest discover
    if %errorlevel%==0 (
        exit /b 0
    ) else (
        exit /b 1
    )
) else (
    :: No tests found, attempt to run main module
    :: Start the main module in background
    start /b cmd /c "python -m app"
    :: Wait 5 seconds
    timeout /t 5 >nul
    :: Kill any python processes started by the main module
    taskkill /im python.exe /f >nul 2>&1
    :: Check if the main module started successfully
    if %errorlevel%==0 (
        exit /b 0
    ) else (
        exit /b 1
    )
)