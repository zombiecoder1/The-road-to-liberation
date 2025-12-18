@echo off
REM Restoration Script for Liberation AI Development Environment
REM ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

echo 🛠️  Liberation AI Development Environment - Restoration Utility
echo ==============================================================
echo.

REM Check if we're in the right directory
if not exist "FIX_PATH_ISSUE.py" (
    echo ❌ ERROR: FIX_PATH_ISSUE.py not found!
    echo    Please run this script from the project root directory.
    echo.
    pause
    exit /b 1
)

echo 🔍 Checking for required directories...
if not exist "Server" (
    echo ⚠️  Warning: Server directory not found
    echo    Creating Server directory...
    mkdir Server
)

if not exist "Adapter" (
    echo ⚠️  Warning: Adapter directory not found
    echo    Creating Adapter directory...
    mkdir Adapter
)

if not exist "Test" (
    echo ⚠️  Warning: Test directory not found
    echo    Creating Test directory...
    mkdir Test
)

echo.
echo 📦 Installing/Updating Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Failed to install/update dependencies
    echo    Continuing with restoration process...
)

echo.
echo ⚙️  Applying configuration fixes...
python FIX_PATH_ISSUE.py
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to apply configuration fixes
    pause
    exit /b 1
)

echo.
echo 🧪 Running verification tests...
python universal_launcher.py --test
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Some tests failed
    echo    Check the comprehensive_test_report.json for details
)

echo.
echo 📋 Summary of actions taken:
echo    1. Verified directory structure
echo    2. Installed/updated dependencies
echo    3. Applied configuration fixes
echo    4. Ran verification tests
echo.
echo 🎉 Restoration process completed!
echo.
echo To start the full system, run:
echo    python universal_launcher.py
echo.
echo To run challenge-based tests, run:
echo    python test_challenge_based.py
echo.
echo 📊 Check the following files for detailed results:
echo    - comprehensive_test_report.json
echo    - launcher.log
echo    - test_results.json
echo.
pause