@echo off
REM Run LocalLLM Optimizer Tests

setlocal enabledelayedexpansion

goto :main

:error
echo [ERROR] %~1
exit /b 1

:main
echo [INFO] Running tests...

REM Activate virtual environment
if not exist "venv" (
    echo [ERROR] Virtual environment not found. Run setup.bat first.
    exit /b 1
)

call venv\Scripts\activate.bat || goto :error "Failed to activate virtual environment"

REM Run pytest
python -m pytest test_optimizer.py -v
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Tests failed
    exit /b 1
)

echo [SUCCESS] All tests passed!
exit /b 0
