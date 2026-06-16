:: run_server.sh - Windows batch compatible script
:: This script sets up environment variables and starts the Flask development server.
:: It is intended to be executed in a Windows command prompt (cmd.exe) or PowerShell.

@echo off
rem ----------------------------------------------------------------------
rem Ensure the script is being run from the project root directory.
rem If not, change to the directory where this script resides.
rem ----------------------------------------------------------------------
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

rem ----------------------------------------------------------------------
rem Set required environment variables for Flask.
rem ----------------------------------------------------------------------
set "FLASK_APP=api.py"
set "FLASK_ENV=development"

rem ----------------------------------------------------------------------
rem Activate a virtual environment if one exists in the project.
rem ----------------------------------------------------------------------
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
) else (
    echo No virtual environment found. Ensure dependencies are installed globally or create one.
)

rem ----------------------------------------------------------------------
rem Install required Python packages if they are missing.
rem ----------------------------------------------------------------------
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installing required Python packages...
    pip install -r requirements.txt
)

rem ----------------------------------------------------------------------
rem Start the Flask development server.
rem ----------------------------------------------------------------------
echo Starting Flask server...
flask run

rem ----------------------------------------------------------------------
rem Return to the original directory.
rem ----------------------------------------------------------------------
popd