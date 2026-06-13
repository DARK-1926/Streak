@echo off
setlocal EnableDelayedExpansion

rem ------------------------------------------------------------
rem  Setup script for llmrender-lite (Windows)
rem ------------------------------------------------------------

rem Ensure we are in the script directory
cd /d "%~dp0"

rem ---- 1. Check for Node.js ---------------------------------------------------
node -v >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed. Please install it from https://nodejs.org/ and retry.
    exit /b 1
) else (
    echo [INFO] Node version: %node_version%
)

rem ---- 2. Create virtual environment (npm) ------------------------------------
if not exist node_modules (
    echo [INFO] Installing npm dependencies...
    npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed.
        exit /b 1
    )
) else (
    echo [INFO] npm dependencies already installed.
)

rem ---- 3. Run tests -----------------------------------------------------------
echo [INFO] Running Jest test suite...
npm test
if errorlevel 1 (
    echo [ERROR] Tests failed.
    exit /b 1
) else (
    echo [SUCCESS] All tests passed.
)

rem ---- 4. Build library (optional) --------------------------------------------
rem Uncomment the next line if you want to verify the build as part of CI
rem npm run build

exit /b 0
