@echo off
echo Building CoFoundersLab Bot Executable...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller

REM Build the executable
echo.
echo Building executable...
pyinstaller --onefile --windowed --name=CoFoundersLab_Bot cofounderslab_bot.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ Executable created successfully!
    echo 📁 Location: dist\CoFoundersLab_Bot.exe
    echo.
    echo 📋 Instructions:
    echo 1. Copy the .exe file to any folder
    echo 2. Make sure Chrome browser is installed
    echo 3. Run the .exe file
    echo 4. The bot will automatically download ChromeDriver
    echo.
    echo Opening dist folder...
    start dist
) else (
    echo.
    echo ❌ Error building executable
)

echo.
pause
