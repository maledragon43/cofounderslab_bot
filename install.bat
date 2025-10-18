@echo off
echo Installing CoFoundersLab Bot Dependencies...
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing required packages...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo Installation completed successfully!
    echo You can now run the bot using: python cofounderslab_bot.py
    echo Or double-click run_bot.bat
) else (
    echo.
    echo Installation failed. Please check the error messages above.
)

echo.
pause
