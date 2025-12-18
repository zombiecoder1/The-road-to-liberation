@echo off
REM Domain Verification Test Runner
REM ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

echo 🚀 Running Domain Verification Tests
echo ====================================

REM Activate virtual environment if it exists
if exist "liberation_env\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call liberation_env\Scripts\activate.bat
)

REM Install required packages if not already installed
echo 🔍 Checking for required packages...
pip show psutil >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing psutil package...
    pip install psutil
)

pip show requests >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing requests package...
    pip install requests
)

REM Run the domain verification tests
echo 🧪 Executing domain verification tests...
python domain_verification_test.py

REM Check the result
if %errorlevel% equ 0 (
    echo ✅ Domain verification tests completed successfully!
) else (
    echo ❌ Domain verification tests encountered errors!
    exit /b %errorlevel%
)

echo 📝 Reports are saved in the current directory
echo ====================================
echo 🎉 Test execution completed!

pause