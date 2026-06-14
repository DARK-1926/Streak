@echo off
rem ------------------------------------------------------------
rem Setup virtual environment and run the test suite for prompt-leak-comment-analyzer
rem ------------------------------------------------------------

rem Create venv in .venv if it does not exist
if not exist .venv (python -m venv .venv)

rem Activate venv
call .venv\Scripts\activate.bat

rem Upgrade pip and install requirements (none beyond stdlib)\r
python -m pip install --upgrade pip

rem Install the package in editable mode
pip install -e .

rem Run tests
python -m unittest discover -v

if %errorlevel% neq 0 (
    echo Tests failed.
    exit /b 1
) else (
    echo All tests passed.
    exit /b 0
)
