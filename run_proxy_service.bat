@echo off
echo ======================================================
echo    The Road to Liberation - Local AI Proxy Service
echo ======================================================
echo.

REM Check if we're in the right directory
if not exist "local_proxy_service.py" (
    echo ERROR: local_proxy_service.py not found!
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
python -c "import ollama, psutil, json, sys, http.server" >nul 2>&1
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

REM Run the proxy service
echo.
echo Starting Local Liberation AI Proxy Service...
echo ===========================================
echo 🚀 Service will be available at http://127.0.0.1:8080
echo 🔒 All data stays local - no cloud transmission
echo 💡 Press Ctrl+C to stop the service
echo.
python local_proxy_service.py

echo.
echo Proxy service execution completed.
pause