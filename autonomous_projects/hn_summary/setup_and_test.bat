@echo off
rem ------------------------------------------------------------
rem hn_summary – self-contained Windows build script
rem ------------------------------------------------------------

rem Create a virtual environment in .venv
python -m venv .venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    exit /b 1
)

rem Activate the venv
call .venv\Scripts\activate.bat

rem Upgrade pip (quietly)
python -m pip install --upgrade pip >nul

rem Install pytest (the only external dependency)
python -m pip install pytest >nul

rem Run the test suite
pytest -q
set "RESULT=%%ERRORLEVEL%%"

rem Deactivate venv
deactivate

if "%RESULT%"=="0" (
    echo All tests passed successfully.
) else (
    echo Tests failed with exit code %RESULT%.
)

exit /b %RESULT%