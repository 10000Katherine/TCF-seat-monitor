@echo off
setlocal

REM Always run from the script directory (handles shortcut launches)
cd /d "%~dp0"

set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY (
    where python >nul 2>&1 && set "PY=python"
)

if not defined PY (
    echo [ERROR] Python not found.
    echo Please install Python 3 and enable PATH, then retry.
    pause
    exit /b 1
)

call %PY% -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Missing tkinter GUI dependency.
    echo Please reinstall Python 3 with Tcl/Tk support, then retry.
    pause
    exit /b 1
)

call %PY% "%~dp0gui_monitor.py"
if errorlevel 1 (
    echo.
    echo [ERROR] GUI failed to start.
    pause
    exit /b 1
)

pause
