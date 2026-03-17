@echo off
title TCF Seat Monitor
echo Installing dependencies...
python -m pip install -r requirements.txt
echo.
echo Starting GUI...
python gui_monitor.py
pause
