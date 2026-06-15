@echo off
REM Setup and test script for ClipSorter
REM Create virtual environment
python -m venv venv
call venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

REM Run tests
python -m pytest tests

REM Exit code reflects test result
 exit /b %errorlevel%