@echooff
setlocal EnableExtensions EnableDelayedExpansionset "EXITCODE=0"

rem ---------- Dependency detection ----------
if exist requirements.txt (
    rem Python virtualenv
    if not exist venv (
        python -m venv venv    )
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if errorlevel 1 set "EXITCODE=1"
) else if exist package.json (
    npm install
    if errorlevel 1 set "EXITCODE=1"
) else (
    echo No requirements.txt or package.json found.
    set "EXITCODE=1"
)

rem ---------- Test or run ----------
if exist test_codeguard.py (
    python -m unittest test_codeguard.py
    if errorlevel 1 set "EXITCODE=1"
) else (
    if exist codeguard.py (
        start "" python codeguard.py
        timeout /t 5 /nobreak >nul
    ) else (
        echo codeguard.py not found.
        set "EXITCODE=1"
    )
)

rem ---------- Exit ----------
exit /b %EXITCODE%