@echo off
echo ============================================================
echo   RIFT REWIND - Backend Server Startup
echo ============================================================
echo.

cd /d "%~dp0"

echo Installing/updating dependencies...
pip install -r requirements.txt --quiet

echo.
echo Starting Flask development server...
echo.

python server.py
