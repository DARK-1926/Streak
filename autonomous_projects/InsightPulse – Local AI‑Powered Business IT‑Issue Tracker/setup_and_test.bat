@echo off
setlocal

rem Check for Windows
if /I "%OS%"=="Windows_NT" (
    echo Detected Windows OS
) else (
    echo This script is designed for Windows. Exiting.
    exit /b 1
)

rem Determine project directory
set SCRIPT_DIR=%~dp0
pushd "%SCRIPT_DIR%"

rem Clean up old .pyc files
del /S /Q *.pyc 2>nul

rem 1. Setup virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        exit /b 1
    )
)

rem Activate virtual environment
call venv\Scripts\activate.bat

rem 2. Install dependencies
if exist requirements.txt (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Dependency installation failed.
        exit /b 1
    )
) else (
    echo No requirements.txt found. Skipping dependency installation.
)

rem 3. Run tests if any
set TESTS_EXIST=0
if exist tests (
    for /f %%i in ('dir /b /s tests\*.py 2^>nul') do (
        set TESTS_EXIST=1
        goto :tests_found
    )
)
:test_not_found
set TESTS_EXIST=0

:tests_found
if %TESTS_EXIST%==1 (
    echo Running unit tests...
    python -m unittest discover -s tests -p "*_test.py"
    if errorlevel 1 (
        echo Tests failed.
        exit /b 1
    ) else (
        echo All tests passed.
    )
) else (
    rem No tests found, run main file for 5 seconds
    if exist app.py (
        echo No tests found. Running app.py for 5 seconds to verify startup...
        start "" cmd /c "timeout /t 5 /nobreak >nul & python app.py"
        timeout /t 5 /nobreak >nul
        if errorlevel 1 (
            echo app.py failed to start.
            exit /b 1
        ) else (
            echo app.py started and exited successfully.
        )
    ) else (
        echo Neither tests nor app.py found. Nothing to run.
    )
)

rem 4. Exit with appropriate code
echo Setup and test completed successfully.
exit /b 0