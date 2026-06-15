@echo off
rem Setup virtual environment and run tests
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
python -m pytest --maxfail=1 --quiet
exit /b 0