@echo off

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies (none required for this demo)

REM Run tests
python -m unittest discover -s tests

REM Exit with appropriate code
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%
exit /b 0