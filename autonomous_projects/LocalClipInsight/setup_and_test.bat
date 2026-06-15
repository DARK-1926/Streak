setup_and_test.bat
@echo off
rem Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat
rem Upgrade pip
python -m pip install --upgrade pip
rem Install dependencies from requirements.txt
python -m pip install -r requirements.txt
rem Run tests
pytest --maxfail=1 --disable-warnings
if %errorlevel% equ 0 (
    echo \nAll tests passed successfully.
    exit /b 0
) else (
    echo \nTests failed.
    exit /b 1
)
