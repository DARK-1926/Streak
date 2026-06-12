@echo off
cd /d D:\Automater

echo Running Autonomous AI Developer... >> run_log.txt
echo Date: %date% %time% >> run_log.txt

:: Check if python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. >> run_log.txt
    exit /b 1
)

:: Run the AI Brain
python ai_brain.py >> run_log.txt 2>&1

echo Finished execution. >> run_log.txt
echo ---------------------------------------- >> run_log.txt
