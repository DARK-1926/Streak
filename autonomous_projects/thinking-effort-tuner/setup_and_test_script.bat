@echo off
REM Create virtual environment
python -m venv venv
REM Activate it
call venv\Scripts\activate
REM Install dependencies
pip install -r requirements.txt
REM Run tests
pytest tests
REM Deactivate
call venv\Scripts\deactivate.bat
exit /b %ERRORLEVEL%
