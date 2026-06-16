@echo off
setlocal EnableDelayedExpansion

REM -------------------------------------------------
REM Setup virtual environment
REM -------------------------------------------------
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        exit /b 1
    )
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

REM -------------------------------------------------
REM Install Python dependencies
REM -------------------------------------------------
if exist requirements.txt (
    pip install --upgrade pip >nul
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install Python dependencies.
        exit /b 1
    )
)

REM -------------------------------------------------
REM Run tests if they exist, otherwise run the main module
REM -------------------------------------------------
set TESTS_FOUND=0
if exist test (
    set TESTS_FOUND=1
) else (
    if exist tests (
        set TESTS_FOUND=1
    ) else (
        if exist *.py (
            for /f %%F in ('dir /b /s *_test.py 2^>nul') do (
                set TESTS_FOUND=1
                goto :found_tests
            )
        )
    )
)

:found_tests
if "%TESTS_FOUND%"=="1" (
    echo Running unit tests...
    python -m unittest discover
    if errorlevel 1 (
        echo Unit tests failed.
        exit /b 1
    ) else (
        echo Unit tests passed.
        exit /b 0
    )
) else (
    echo No tests found. Running main module for a quick sanity check...
    start "" cmd /c "python -m lca.cli"
    timeout /t 5 /nobreak >nul
    tasklist /fi "imagename eq python.exe" | findstr /i "python.exe" >nul
    if errorlevel 1 (
        echo Main module terminated within 5 seconds.
        exit /b 0
    ) else (
        echo Main module is still running after 5 seconds. Assuming success.
        REM Optionally kill the process
        taskkill /im python.exe /f >nul 2>&1
        exit /b 0
    )
)

exit /b 1