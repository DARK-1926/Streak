@echo off
setlocal EnableDelayedExpansion

:: ------------------------------------------------------------
:: Create virtual environment
:: ------------------------------------------------------------
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    exit /b 1
)

:: Activate venv
call venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

:: Upgrade pip and install dependencies
python -m pip install --upgrade pip setuptools wheel >NUL
python -m pip install -r requirements.txt >NUL
if errorlevel 1 (
    echo Dependency installation failed.
    exit /b 1
)

:: Run tests
python -m pytest -q
if %ERRORLEVEL% EQU 0 (
    echo All tests passed.
    exit /b 0
) else (
    echo Tests failed.
    exit /b 1
)
