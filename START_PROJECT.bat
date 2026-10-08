@echo off
setlocal
cd /d "%~dp0"

echo ================================================
echo Fitness Activity Tracker - Starting Application
echo ================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found in PATH.
    echo Install Python 3.10 or newer from python.org and enable "Add Python to PATH".
    pause
    exit /b 1
)

echo Installing/checking required packages...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Required packages could not be installed.
    pause
    exit /b 1
)

echo.
echo Starting the project...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo The application exited with an error.
    pause
)
endlocal
