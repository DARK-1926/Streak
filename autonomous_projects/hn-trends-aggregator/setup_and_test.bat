@echo off
rem === Windows batch script to set up virtual environment and run tests ===
python -m venv .venv
if %errorlevel% neq 0 exit /b %errorlevel%
call .venv\Scripts\activate.bat
pip install --quiet -r requirements.txt
pip install --quiet pytest
pytest
exit /b 0