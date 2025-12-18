@echo off
echo ======================================================
echo    The Road to Liberation - Demo Usage
echo ======================================================
echo.

REM Check if we're in the right directory
if not exist "demo_usage.py" (
    echo ERROR: demo_usage.py not found!
    echo Please run this script from the project directory.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call liberation_env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    echo Please make sure liberation_env exists and is properly set up
    echo.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import ollama, psutil, json, sys, requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install required packages
        echo.
        pause
        exit /b 1
    )
)

REM Run the demo
echo.
echo Starting Demo Usage...
echo ====================
python demo_usage.py

echo.
echo Demo execution completed.
pause