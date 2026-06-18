@echo off
setlocal

REM Check for Python
where python >nul 2>&1
if errorlevel 1 (
    echo Python not found.
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

REM Install dependencies
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies.
        exit /b 1
    )
)

REM Check for tests
set TESTS_EXIST=0
for %%f in (test_*.py) do (
    set TESTS_EXIST=1
    goto :tests_found
)
for /d %%d in (tests) do (
    if exist "%%d\*.py" (
        set TESTS_EXIST=1
        goto :tests_found
    )
)
:tests_found

if %TESTS_EXIST%==1 (
    REM Run tests
    python -m unittest discover
    if errorlevel 1 (
        echo Tests failed.
        exit /b 1
    )
) else (
    REM No tests found, run main file for 5 seconds
    start "" python app.py
    timeout /t 5 /nobreak >nul
    taskkill /f /im python.exe >nul 2>&1
)

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

exit /b 0