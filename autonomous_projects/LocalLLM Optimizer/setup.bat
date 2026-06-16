@echo off
setlocal

:: Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat

:: Upgrade pip
pip install --upgrade pip

:: Install dependencies
pip install -r requirements.txt

:: Install test dependencies
pip install pytest

:: Run tests
pytest
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

:: Success
exit /b 0
