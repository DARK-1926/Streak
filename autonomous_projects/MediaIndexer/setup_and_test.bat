@echo off
REM Setup virtual environment and run tests
python -m venv .venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    exit /b 1
)
call .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    exit /b 1
)
pytest
if errorlevel 1 (
    echo Tests failed.
    exit /b 1
)
echo All tests passed.
exit /b 0
