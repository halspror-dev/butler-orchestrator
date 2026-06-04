@echo off
cd /d "%~dp0"
echo === Butler ===
echo Activating environment and starting the server...
call venv\Scripts\activate.bat
python server.py
pause