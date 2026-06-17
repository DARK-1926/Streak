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

REM Activate venv
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

REM -------------------------------------------------
REM Install dependencies
REM -------------------------------------------------
if exist requirements.txt (
    pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Dependency installation failed.
        exit /b 1
    )
) else (
    echo No requirements.txt found, skipping pip install.
)

REM -------------------------------------------------
REM Run tests if any
REM -------------------------------------------------
set TESTS_FOUND=0
for /f %%i in ('dir /b /s *_test.py 2^>nul') do (
    set TESTS_FOUND=1
    goto :run_tests
)
for /f %%i in ('dir /b /s test_*.py 2^>nul') do (
    set TESTS_FOUND=1
    goto :run_tests
)

:run_tests
if "!TESTS_FOUND!"=="1" (
    echo Running unit tests...
    python -m unittest discover
    if errorlevel 1 (
        echo Tests failed.
        exit /b 1
    ) else (
        echo Tests passed.
        exit /b 0
    )
)

REM -------------------------------------------------
REM No tests found – run main.py for 5 seconds
REM -------------------------------------------------
if exist main.py (
    echo No tests detected. Running main.py for 5 seconds...
    start "" /b cmd /c "python main.py"
    timeout /t 5 >nul
    taskkill /im python.exe /f >nul 2>&1
    if errorlevel 1 (
        echo Failed to terminate main.py process.
        exit /b 1
    )
    echo main.py executed successfully for 5 seconds.
    exit /b 0
) else (
    echo main.py not found.
    exit /b 1
)