@echo off
rem Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat
rem Upgrade pip
python -m pip install --upgrade pip
rem Install dependencies
pip install -r requirements.txt
rem Run tests
pytest --maxfail=1 --disable-warnings
if %errorlevel% equ 0 (
    echo All tests passed.
    exit /b 0
) else (
    echo Tests failed.
    exit /b 1
)