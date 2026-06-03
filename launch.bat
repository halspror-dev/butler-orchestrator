@echo off
cd /d "%~dp0"
echo === Butler ===
echo Activating environment and starting the UI...
call venv\Scripts\activate.bat
python ui.py
pause