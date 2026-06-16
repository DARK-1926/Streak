@echo off
REM Create virtual environment
python -m venv venv
if %ERRORLEVEL% neq 0 exit /b 1

REM Activate venv
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 exit /b 1

REM Check for tests
if exist test_api.py (
    python -m unittest discover -s . -p "test_*.py"
    if %ERRORLEVEL% neq 0 exit /b 1
) else (
    python -c "import time; import model_loader; import api; time.sleep(5)"
    if %ERRORLEVEL% neq 0 exit /b 1
)

REM Success
exit /b 0