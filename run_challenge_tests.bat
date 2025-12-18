@echo off
REM Challenge-Based Tests Runner for Universal Launcher
REM ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

echo 🚀 Running Challenge-Based Tests for Universal Launcher
echo =======================================================

REM Activate virtual environment if it exists
if exist "liberation_env\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call liberation_env\Scripts\activate.bat
)

REM Install required packages if not already installed
echo 🔍 Checking for required packages...
pip show psutil >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing required packages...
    pip install psutil
)

REM Run the challenge-based tests
echo 🧪 Executing challenge-based tests...
python test_challenge_based.py

REM Check the result
if %errorlevel% equ 0 (
    echo ✅ Challenge tests completed successfully!
) else (
    echo ❌ Challenge tests encountered errors!
    exit /b %errorlevel%
)

echo 📝 Reports are saved in the current directory
echo =======================================================
echo 🎉 Test execution completed!

pause