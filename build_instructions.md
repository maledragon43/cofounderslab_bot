# Building CoFoundersLab Bot Executable

This guide will help you create a standalone executable (.exe) file from the CoFoundersLab Bot.

## Method 1: Using the Batch File (Recommended for Windows)

1. **Double-click `build_exe.bat`**
   - This will automatically install PyInstaller and build the executable
   - The executable will be created in the `dist` folder

## Method 2: Using Python Script

1. **Run the build script:**
   ```bash
   python build_exe.py
   ```

## Method 3: Manual Build

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable:**
   ```bash
   pyinstaller --onefile --windowed --name=CoFoundersLab_Bot cofounderslab_bot.py
   ```

## After Building

### Files Created:
- `dist/CoFoundersLab_Bot.exe` - The standalone executable
- `build/` - Temporary build files (can be deleted)
- `CoFoundersLab_Bot.spec` - PyInstaller spec file (can be deleted)

### Distribution:
1. **Copy the .exe file** to any folder on any Windows computer
2. **No Python installation required** on the target computer
3. **Chrome browser must be installed** on the target computer
4. **The bot will automatically download ChromeDriver** when first run

### Requirements for Target Computer:
- ✅ Windows 7/8/10/11
- ✅ Chrome browser installed
- ✅ Internet connection (for ChromeDriver download)
- ❌ Python NOT required
- ❌ Dependencies NOT required

## Troubleshooting

### If build fails:
1. **Update pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Install dependencies first:**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. **Try building with console window:**
   ```bash
   pyinstaller --onefile --name=CoFoundersLab_Bot cofounderslab_bot.py
   ```

### If executable doesn't work:
1. **Check Chrome is installed**
2. **Run as administrator**
3. **Check Windows Defender/Antivirus** (may block the .exe)

## File Size
- The executable will be approximately 15-20 MB
- This includes Python runtime and all dependencies

## Security Note
- Some antivirus software may flag the .exe as suspicious
- This is normal for PyInstaller executables
- You may need to add an exception in your antivirus
